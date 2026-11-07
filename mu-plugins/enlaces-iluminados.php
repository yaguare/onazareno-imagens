<?php
/**
 * Plugin Name: Enlaces iluminados
 * Description: Índice de uma série de posts (1-150, capítulos, códigos...) em que cada item vira link FIXO no conteúdo da página no momento em que o post correspondente é publicado. Uso: [enlaces_iluminados slug="salmo-{n}" desde="1" hasta="150"] numa página.
 * Version: 1.3.0
 *
 * Como funciona
 * - A configuração fica no próprio shortcode, dentro da página (o mesmo arquivo serve para qualquer site).
 * - Quando um post é publicado, despublicado ou muda de slug, o plugin reescreve o HTML do índice
 *   DENTRO do conteúdo das páginas que têm o shortcode: [enlaces_iluminados ...]HTML com os links[/enlaces_iluminados].
 * - Na visita, o shortcode só devolve esse HTML já gravado: nenhuma consulta ao banco.
 *
 * Atributos
 *   slug      Padrão do slug, com {n} no lugar do número. Obrigatório. Ex.: salmo-{n}
 *   desde     Primeiro número (padrão 1).
 *   hasta     Último número. Obrigatório.
 *   tipo      Post type dos itens (padrão post).
 *   grupos    Blocos com título: "1-41:Livro I|42-72:Livro II". Sem grupos, uma grade só.
 *   titulo    Texto do title de cada link, com {n} (padrão "{n}").
 *   resumo    Frase acima da grade, com {x} (publicados) e {total}. Vazio = sem frase.
 *   pendente  Title dos números ainda não publicados (padrão vazio).
 *   cor       Cor dos números com link (padrão #b8913a).
 *
 * Modo lista (1.1.0) — séries com nome em vez de número (signos, meses, animais...):
 *   itens     "chave:Rótulo|chave:Rótulo". A chave substitui {n} no slug; o rótulo vira {t}.
 *             Com itens, desde/hasta/grupos são ignorados.
 *   texto     Texto visível de cada item, com {t} e {n} (padrão "{t}").
 *   estilo    "grade" (quadradinhos, padrão no modo numérico) ou "lista" (ul simples que
 *             herda o estilo do tema; padrão no modo itens).
 *   classe    Classes extras do <ul> no estilo lista (ex.: "wp-block-list alfa-grilla-signos").
 *   titulo/pendente também aceitam {t}.
 *
 * Modo em linha (1.2.0) — um link solto dentro de uma frase:
 *   [enlace_iluminado slug="signo-20-de-abril"]20 de abril[/enlace_iluminado]
 *   Enquanto o post não existe, mostra só o texto; ao publicar, o <a href> é gravado no conteúdo.
 *   Atributos: slug (exato, sem {n}), tipo (padrão post).
 *
 * Marcado automático (1.3.0) — mapa de entidades por site:
 *   - O mapa (option ei_mapa: [forma, slug] + tope) é carregado pela ability enlaces-iluminados/cargar-mapa,
 *     que baixa um JSON de raw.githubusercontent.com. Sem mapa, o site não marca nada.
 *   - Cada post (post_type post) salvo como publish/future é marcado antes de gravar: cada forma do mapa
 *     vira [enlace_iluminado slug="..."]forma[/enlace_iluminado].
 *   - Regras: ganha a forma mais longa; só a primeira aparição de cada slug; nunca o próprio slug;
 *     nunca em títulos h1-h6, <script>, <style>, <a>, comentários, shortcodes nem atributos; maiúsculas
 *     exatas; tope de marcas por post (contando as que já havia).
 *   - Meta _ei_no_marcar = 1 num post desliga o marcado automático nele.
 *   - Ability enlaces-iluminados/marcar-posts: marca posts já existentes (dry_run por padrão).
 *   - Ao publicar/despublicar um post, só se reescrevem os posts que apontam para ele (e os índices).
 */
if (!defined('ABSPATH')) exit;

const EI_TAG = 'enlaces_iluminados';
const EI_TAG_LINHA = 'enlace_iluminado';

function ei_tem_tag($c) {
    return strpos($c, '[' . EI_TAG) !== false || strpos($c, '[' . EI_TAG_LINHA) !== false;
}

/* Visita (modo em linha): devolve o texto ou o link gravado. */
add_shortcode(EI_TAG_LINHA, function ($atts, $content = null) {
    return (string) $content;
});

/* Reescreve os links em linha de um conteúdo, com uma consulta só para todos os slugs. */
function ei_reescrever_linha($conteudo) {
    if (strpos($conteudo, '[' . EI_TAG_LINHA) === false) return $conteudo;
    $regex = get_shortcode_regex([EI_TAG_LINHA]);
    if (!preg_match_all("/$regex/s", $conteudo, $todos, PREG_SET_ORDER)) return $conteudo;
    $por_tipo = [];
    foreach ($todos as $m) {
        if ($m[1] === '[' && $m[6] === ']') continue;
        $a = shortcode_parse_atts($m[3]);
        $slug = isset($a['slug']) ? sanitize_title($a['slug']) : '';
        $tipo = isset($a['tipo']) ? sanitize_key($a['tipo']) : 'post';
        if ($slug !== '') $por_tipo[$tipo][$slug] = true;
    }
    global $wpdb;
    $links = [];
    foreach ($por_tipo as $tipo => $slugs) {
        foreach (array_chunk(array_keys($slugs), 500) as $lote) {
            $ph   = implode(',', array_fill(0, count($lote), '%s'));
            $rows = $wpdb->get_results($wpdb->prepare(
                "SELECT ID, post_name FROM {$wpdb->posts} WHERE post_status = 'publish' AND post_type = %s AND post_name IN ($ph)",
                array_merge([$tipo], $lote)
            ));
            foreach ($rows as $r) $links[$tipo . '|' . $r->post_name] = get_permalink((int) $r->ID);
        }
    }
    return preg_replace_callback("/$regex/s", function ($m) use ($links) {
        if ($m[1] === '[' && $m[6] === ']') return $m[0];
        $a = shortcode_parse_atts($m[3]);
        $slug = isset($a['slug']) ? sanitize_title($a['slug']) : '';
        $tipo = isset($a['tipo']) ? sanitize_key($a['tipo']) : 'post';
        $texto = trim(wp_strip_all_tags((string) $m[5]));
        $dentro = isset($links[$tipo . '|' . $slug])
            ? '<a href="' . esc_url($links[$tipo . '|' . $slug]) . '">' . esc_html($texto) . '</a>'
            : esc_html($texto);
        return '[' . EI_TAG_LINHA . $m[3] . ']' . $dentro . '[/' . EI_TAG_LINHA . ']';
    }, $conteudo);
}

/* Visita: devolve o HTML gravado. */
add_shortcode(EI_TAG, function ($atts, $content = null) {
    return (string) $content;
});

/* Monta o HTML de um índice a partir dos atributos. */
function ei_montar($a) {
    $a = shortcode_atts([
        'slug' => '', 'desde' => 1, 'hasta' => 0, 'tipo' => 'post', 'grupos' => '',
        'titulo' => '{n}', 'resumo' => '', 'pendente' => '', 'cor' => '#b8913a',
        'itens' => '', 'texto' => '{t}', 'estilo' => '', 'classe' => '',
    ], (array) $a);
    if ($a['slug'] === '' || strpos($a['slug'], '{n}') === false) {
        return '<p class="ei-erro">Enlaces iluminados: configuração inválida (slug com {n}).</p>';
    }

    // Itens: chave => rótulo. Modo numérico: o número é chave e rótulo.
    $itens = [];
    if (trim($a['itens']) !== '') {
        foreach (explode('|', $a['itens']) as $it) {
            $p = explode(':', $it, 2);
            $k = trim($p[0]);
            if ($k === '') continue;
            $itens[$k] = isset($p[1]) ? trim($p[1]) : $k;
        }
        if (!$itens || count($itens) > 5000) return '<p class="ei-erro">Enlaces iluminados: itens inválidos.</p>';
        $modo_itens = true;
    } else {
        $desde = (int) $a['desde'];
        $hasta = (int) $a['hasta'];
        if ($hasta < $desde || $hasta - $desde > 5000) {
            return '<p class="ei-erro">Enlaces iluminados: configuração inválida (desde, hasta).</p>';
        }
        for ($n = $desde; $n <= $hasta; $n++) $itens[(string) $n] = (string) $n;
        $modo_itens = false;
    }
    $estilo = $a['estilo'] !== '' ? $a['estilo'] : ($modo_itens ? 'lista' : 'grade');

    $slugs = [];
    foreach ($itens as $k => $t) {
        $slugs[$k] = sanitize_title(str_replace('{n}', (string) $k, $a['slug']));
    }

    global $wpdb;
    $links = [];
    foreach (array_chunk(array_values($slugs), 500) as $lote) {
        $ph   = implode(',', array_fill(0, count($lote), '%s'));
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT ID, post_name FROM {$wpdb->posts} WHERE post_status = 'publish' AND post_type = %s AND post_name IN ($ph)",
            array_merge([sanitize_key($a['tipo'])], $lote)
        ));
        foreach ($rows as $r) $links[$r->post_name] = get_permalink((int) $r->ID);
    }

    $total = count($itens);
    $x = 0;
    foreach ($slugs as $s) if (isset($links[$s])) $x++;
    $troca = function ($modelo, $k) use ($itens) {
        return str_replace(['{n}', '{t}'], [(string) $k, $itens[$k]], $modelo);
    };
    $resumo = trim($a['resumo']) !== ''
        ? '<p class="ei-resumo">' . str_replace(['{x}', '{total}'], ['<strong>' . $x . '</strong>', '<strong>' . $total . '</strong>'], esc_html($a['resumo'])) . '</p>'
        : '';

    if ($estilo === 'lista') {
        $classe = trim('ei-lista ' . preg_replace('/[^A-Za-z0-9_\- ]/', '', $a['classe']));
        $out = '<ul class="' . esc_attr($classe) . '">';
        foreach ($itens as $k => $t) {
            $txt = esc_html($troca($a['texto'], $k));
            $s = $slugs[$k];
            if (isset($links[$s])) {
                $tit = $troca($a['titulo'], $k);
                $out .= '<li><a href="' . esc_url($links[$s]) . '"' . ($a['titulo'] !== '{n}' ? ' title="' . esc_attr($tit) . '"' : '') . '>' . $txt . '</a></li>';
            } else {
                $out .= '<li>' . ($a['pendente'] !== '' ? '<span title="' . esc_attr($troca($a['pendente'], $k)) . '">' . $txt . '</span>' : $txt) . '</li>';
            }
        }
        return $resumo . $out . '</ul>';
    }

    if ($modo_itens) {
        $out = '<div class="ei-indice" style="--ei-cor:' . (sanitize_hex_color($a['cor']) ?: '#b8913a') . '">' . $resumo . '<ul class="ei-grade">';
        foreach ($itens as $k => $t) {
            $txt = esc_html($troca($a['texto'], $k));
            $s = $slugs[$k];
            $out .= isset($links[$s])
                ? '<li><a href="' . esc_url($links[$s]) . '" title="' . esc_attr($troca($a['titulo'], $k)) . '">' . $txt . '</a></li>'
                : '<li><span' . ($a['pendente'] !== '' ? ' title="' . esc_attr($troca($a['pendente'], $k)) . '"' : '') . '>' . $txt . '</span></li>';
        }
        return $out . '</ul></div>';
    }

    $grupos = [];
    if (trim($a['grupos']) !== '') {
        foreach (explode('|', $a['grupos']) as $g) {
            if (preg_match('/^\s*(\d+)\s*-\s*(\d+)\s*:(.*)$/s', $g, $m)) $grupos[] = [(int) $m[1], (int) $m[2], trim($m[3])];
        }
    }
    if (!$grupos) $grupos[] = [$desde, $hasta, ''];

    $cor = sanitize_hex_color($a['cor']) ?: '#b8913a';
    $out = '<div class="ei-indice" style="--ei-cor:' . $cor . '">' . $resumo;
    foreach ($grupos as $g) {
        if ($g[2] !== '') $out .= '<p class="ei-grupo">' . esc_html($g[2]) . '</p>';
        $out .= '<ul class="ei-grade">';
        for ($n = max($g[0], $desde); $n <= min($g[1], $hasta); $n++) {
            $s = $slugs[(string) $n];
            if (isset($links[$s])) {
                $out .= '<li><a href="' . esc_url($links[$s]) . '" title="' . esc_attr(str_replace('{n}', $n, $a['titulo'])) . '">' . $n . '</a></li>';
            } else {
                $out .= '<li><span' . ($a['pendente'] !== '' ? ' title="' . esc_attr($a['pendente']) . '"' : '') . '>' . $n . '</span></li>';
            }
        }
        $out .= '</ul>';
    }
    return $out . '</div>';
}

/* Reescreve os índices de um conteúdo. Devolve o conteúdo novo. */
function ei_reescrever_conteudo($conteudo) {
    $conteudo = ei_reescrever_linha($conteudo);
    if (strpos($conteudo, '[' . EI_TAG) === false) return $conteudo;
    $regex = get_shortcode_regex([EI_TAG]);
    return preg_replace_callback("/$regex/s", function ($m) {
        if ($m[1] === '[' && $m[6] === ']') return $m[0]; // [[escapado]]
        $abre = '[' . $m[2] . $m[3] . ']';
        $abre = preg_replace('/\s*\/\]$/', ']', $abre);
        return $abre . ei_montar(shortcode_parse_atts($m[3])) . '[/' . EI_TAG . ']';
    }, $conteudo);
}

/* Reescreve todas as páginas/posts que usam o shortcode. */
function ei_reescrever_tudo() {
    global $wpdb;
    $like  = '%' . $wpdb->esc_like('[' . EI_TAG) . '%';
    $like2 = '%' . $wpdb->esc_like('[' . EI_TAG_LINHA) . '%';
    $ids  = $wpdb->get_col($wpdb->prepare(
        "SELECT ID FROM {$wpdb->posts} WHERE (post_content LIKE %s OR post_content LIKE %s) AND post_status IN ('publish','draft','future','pending','private') AND post_type NOT IN ('revision','nav_menu_item')",
        $like, $like2
    ));
    foreach ($ids as $id) {
        $atual = get_post_field('post_content', $id, 'raw');
        $novo  = ei_reescrever_conteudo($atual);
        if ($novo !== $atual) {
            // Direto no banco: sem revisões, sem hooks e sem kses (no cron não há usuário).
            $wpdb->update($wpdb->posts, ['post_content' => $novo], ['ID' => $id]);
            clean_post_cache($id);
        }
    }
}

/* Reescreve uma lista de IDs. */
function ei_reescrever_ids($ids) {
    global $wpdb;
    foreach (array_unique(array_map('intval', $ids)) as $id) {
        if ($id <= 0) continue;
        $atual = get_post_field('post_content', $id, 'raw');
        if (!is_string($atual) || !ei_tem_tag($atual)) continue;
        $novo = ei_reescrever_conteudo($atual);
        if ($novo !== $atual) {
            $wpdb->update($wpdb->posts, ['post_content' => $novo], ['ID' => $id]);
            clean_post_cache($id);
        }
    }
}

/* Pendências do request: tudo, ou só os posts que apontam para certos slugs + IDs avulsos. */
$GLOBALS['ei_pend'] = ['tudo' => false, 'slugs' => [], 'ids' => []];

function ei_agendar($slugs = null, $ids = []) {
    static $hook = false;
    if ($slugs === null) {
        $GLOBALS['ei_pend']['tudo'] = true;
    } else {
        foreach ((array) $slugs as $s) if ($s !== '') $GLOBALS['ei_pend']['slugs'][$s] = true;
    }
    foreach ((array) $ids as $i) $GLOBALS['ei_pend']['ids'][(int) $i] = true;
    if (!$hook) {
        $hook = true;
        add_action('shutdown', 'ei_processar_pendentes');
    }
}

function ei_processar_pendentes() {
    $p = $GLOBALS['ei_pend'];
    $GLOBALS['ei_pend'] = ['tudo' => false, 'slugs' => [], 'ids' => []];
    if ($p['tudo']) {
        ei_reescrever_tudo();
        return;
    }
    global $wpdb;
    $ids = array_keys($p['ids']);
    if ($p['slugs']) {
        // Índices (poucas páginas): sempre, porque dependem de padrões de slug.
        $ids = array_merge($ids, $wpdb->get_col($wpdb->prepare(
            "SELECT ID FROM {$wpdb->posts} WHERE post_content LIKE %s AND post_status IN ('publish','draft','future','pending','private') AND post_type NOT IN ('revision','nav_menu_item')",
            '%' . $wpdb->esc_like('[' . EI_TAG . ' ') . '%'
        )));
        // Links em linha: só os posts que citam esses slugs.
        foreach (array_keys($p['slugs']) as $s) {
            $ids = array_merge($ids, $wpdb->get_col($wpdb->prepare(
                "SELECT ID FROM {$wpdb->posts} WHERE post_content LIKE %s AND post_status IN ('publish','draft','future','pending','private') AND post_type NOT IN ('revision','nav_menu_item')",
                '%' . $wpdb->esc_like('slug="' . $s . '"') . '%'
            )));
        }
    }
    ei_reescrever_ids($ids);
}

/* Gatilhos: publicação/despublicação, troca de slug e posts com o shortcode salvos. */
add_action('transition_post_status', function ($novo, $antigo, $post) {
    if ($novo === $antigo || in_array($post->post_type, ['revision', 'nav_menu_item'], true)) return;
    if ($novo === 'publish' || $antigo === 'publish') ei_agendar([$post->post_name], [$post->ID]);
}, 10, 3);

add_action('post_updated', function ($id, $depois, $antes) {
    if ($depois->post_status === 'publish' && $depois->post_name !== $antes->post_name) {
        ei_agendar([$depois->post_name, $antes->post_name], [$id]);
    }
}, 10, 3);

add_action('save_post', function ($id, $post) {
    if (wp_is_post_revision($id)) return;
    if (ei_tem_tag((string) $post->post_content)) ei_agendar([], [$id]);
}, 10, 2);

/* ===================== Marcado automático (1.3.0) ===================== */

const EI_PROTEGIDAS = '~<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<h([1-6])\b.*?</h\1>|<a\b.*?</a>|\[enlaces_iluminados\b.*?\[/enlaces_iluminados\]|\[enlace_iluminado\b.*?\[/enlace_iluminado\]|\[[^\]]*\]|<[^>]+>~isu';

/* Mapa carregado: ['tope' => int, 'entradas' => [[forma, slug], ...]] ou null. */
function ei_mapa() {
    static $m = false;
    if ($m === false) {
        $o = get_option('ei_mapa');
        $m = (is_array($o) && !empty($o['entradas'])) ? $o : null;
    }
    return $m;
}

/* Regex de uma forma: limites de palavra Unicode, espaços flexíveis, maiúsculas exatas. */
function ei_regex_forma($forma) {
    $partes = preg_split('/\s+/u', trim($forma), -1, PREG_SPLIT_NO_EMPTY);
    $partes = array_map(function ($p) { return preg_quote($p, '~'); }, $partes);
    return '~(?<![\p{L}\p{N}_])' . implode('\s+', $partes) . '(?![\p{L}\p{N}_])~u';
}

/**
 * Marca um conteúdo. Devolve [conteudo_novo, [[texto, slug], ...]].
 */
function ei_marcar($html, $slug_proprio = '', $mapa = null) {
    $mapa = $mapa ?: ei_mapa();
    if (!$mapa || !is_string($html) || $html === '') return [$html, []];
    $tope = isset($mapa['tope']) ? (int) $mapa['tope'] : 30;

    preg_match_all('/\[enlace_iluminado\s+slug="([^"]+)"/', $html, $ja);
    $usados = array_fill_keys($ja[1], true);
    if ($slug_proprio !== '') $usados[$slug_proprio] = true;
    $existentes = count($ja[1]);
    if ($existentes >= $tope) return [$html, []];

    // Cópia com as zonas protegidas tapadas (mesmo tamanho em bytes, offsets válidos).
    $livre = preg_replace_callback(EI_PROTEGIDAS, function ($m) {
        return str_repeat("\x01", strlen($m[0]));
    }, $html);
    if (!is_string($livre)) return [$html, []];

    $cand = [];
    foreach ($mapa['entradas'] as $e) {
        list($forma, $slug) = $e;
        // Sin descartar slugs ya usados: igual compiten por largo (así "Capricornio" dentro de
        // "horóscopo Capricornio 2027", que es el propio post, no se marca suelto).
        $prim = strtok($forma, ' ');
        if ($prim === false || strpos($livre, $prim) === false) continue; // pré-filtro barato
        if (!preg_match_all(ei_regex_forma($forma), $livre, $mm, PREG_OFFSET_CAPTURE)) continue;
        foreach ($mm[0] as $x) {
            $cand[] = [$x[1], $x[1] + strlen($x[0]), $slug, mb_strlen($x[0], 'UTF-8')];
        }
    }
    if (!$cand) return [$html, []];

    // 1) Ganha a forma mais longa em cada sobreposição.
    usort($cand, function ($a, $b) { return $b[3] <=> $a[3] ?: $a[0] <=> $b[0]; });
    $ganha = [];
    foreach ($cand as $c) {
        foreach ($ganha as $g) {
            if ($c[0] < $g[1] && $g[0] < $c[1]) continue 2;
        }
        $ganha[] = $c;
    }

    // 2) Primeira aparição de cada slug, com tope.
    usort($ganha, function ($a, $b) { return $a[0] <=> $b[0]; });
    $escolhidos = [];
    foreach ($ganha as $c) {
        if (isset($usados[$c[2]])) continue;
        if ($existentes + count($escolhidos) >= $tope) break;
        $usados[$c[2]] = true;
        $escolhidos[] = $c;
    }

    // 3) Reescrita de trás para frente.
    $out = $html;
    $marcas = [];
    foreach (array_reverse($escolhidos) as $c) {
        $txt = substr($html, $c[0], $c[1] - $c[0]);
        $out = substr($out, 0, $c[0]) . '[' . EI_TAG_LINHA . ' slug="' . $c[2] . '"]' . $txt . '[/' . EI_TAG_LINHA . ']' . substr($out, $c[1]);
        array_unshift($marcas, [$txt, $c[2]]);
    }
    return [$out, $marcas];
}

/* Antes de gravar: marca posts publicados ou agendados. */
add_filter('wp_insert_post_data', function ($data, $postarr) {
    if (!ei_mapa()) return $data;
    if (($data['post_type'] ?? '') !== 'post') return $data;
    if (!in_array($data['post_status'] ?? '', ['publish', 'future'], true)) return $data;
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return $data;
    $id = isset($postarr['ID']) ? (int) $postarr['ID'] : 0;
    if ($id && get_post_meta($id, '_ei_no_marcar', true)) return $data;
    $conteudo = wp_unslash($data['post_content']);
    list($novo, $marcas) = ei_marcar($conteudo, (string) ($data['post_name'] ?? ''));
    if ($marcas) $data['post_content'] = wp_slash($novo);
    return $data;
}, 20, 2);

/* ===================== Abilities (MCP) ===================== */

add_action('wp_abilities_api_categories_init', function () {
    if (function_exists('wp_register_ability_category')) {
        wp_register_ability_category('enlaces-iluminados', [
            'label'       => 'Enlaces iluminados',
            'description' => 'Mapa de entidades y marcado automático de enlaces internos.',
        ]);
    }
});

add_action('wp_abilities_api_init', function () {
    if (!function_exists('wp_register_ability')) return;
    $meta = function ($readonly) {
        return [
            'annotations'  => ['readonly' => $readonly, 'destructive' => false, 'idempotent' => true],
            'show_in_rest' => true,
            'public'       => true,
            'mcp'          => ['public' => true],
        ];
    };
    $pode = function () { return current_user_can('edit_others_posts'); };

    wp_register_ability('enlaces-iluminados/cargar-mapa', [
        'label'       => 'Cargar el mapa de entidades',
        'description' => 'Descarga el mapa de entidades (JSON con "tope" y "entradas": [[forma, slug], ...]) desde una URL de raw.githubusercontent.com y lo guarda en el sitio. Desde ese momento, cada post que se publique o programe se marca solo. No toca los posts existentes (para eso, marcar-posts).',
        'category'    => 'enlaces-iluminados',
        'input_schema' => [
            'type' => 'object',
            'properties' => ['url' => ['type' => 'string', 'description' => 'URL https de raw.githubusercontent.com (mejor con el hash del commit).']],
            'required' => ['url'],
        ],
        'output_schema' => ['type' => 'object'],
        'permission_callback' => $pode,
        'execute_callback' => function ($in = []) {
            $in = (array) $in;
            $url = isset($in['url']) ? (string) $in['url'] : '';
            if (wp_parse_url($url, PHP_URL_HOST) !== 'raw.githubusercontent.com' || wp_parse_url($url, PHP_URL_SCHEME) !== 'https') {
                return new WP_Error('ei_url', 'Solo se aceptan URLs https de raw.githubusercontent.com.');
            }
            $r = wp_remote_get($url, ['timeout' => 30]);
            if (is_wp_error($r)) return $r;
            if (wp_remote_retrieve_response_code($r) !== 200) return new WP_Error('ei_http', 'HTTP ' . wp_remote_retrieve_response_code($r));
            $j = json_decode(wp_remote_retrieve_body($r), true);
            if (!is_array($j) || empty($j['entradas']) || !is_array($j['entradas'])) return new WP_Error('ei_json', 'JSON inválido: falta "entradas".');
            $ent = [];
            $slugs = [];
            foreach ($j['entradas'] as $e) {
                if (!is_array($e) || count($e) < 2) continue;
                $f = trim((string) $e[0]);
                $s = sanitize_title((string) $e[1]);
                if ($f === '' || $s === '') continue;
                $ent[] = [$f, $s];
                $slugs[$s] = true;
            }
            if (!$ent || count($ent) > 50000) return new WP_Error('ei_json', 'Cantidad de entradas inválida.');
            $tope = isset($j['tope']) ? max(1, min(200, (int) $j['tope'])) : 30;
            $mapa = ['version' => (string) ($j['version'] ?? ''), 'url' => $url, 'tope' => $tope, 'entradas' => $ent, 'cargado' => current_time('mysql')];
            update_option('ei_mapa', $mapa, false);
            return ['version' => $mapa['version'], 'tope' => $tope, 'formas' => count($ent), 'slugs' => count($slugs)];
        },
        'meta' => $meta(false),
    ]);

    wp_register_ability('enlaces-iluminados/estado-mapa', [
        'label'       => 'Ver el mapa cargado',
        'description' => 'Devuelve la versión, la URL, el tope y la cantidad de formas y slugs del mapa de entidades cargado en el sitio.',
        'category'    => 'enlaces-iluminados',
        'input_schema' => ['type' => 'object', 'properties' => new stdClass()],
        'output_schema' => ['type' => 'object'],
        'permission_callback' => $pode,
        'execute_callback' => function ($in = []) {
            $m = get_option('ei_mapa');
            if (!is_array($m)) return ['cargado' => false];
            return ['cargado' => true, 'version' => $m['version'] ?? '', 'url' => $m['url'] ?? '', 'tope' => $m['tope'] ?? 30,
                    'formas' => count($m['entradas']), 'slugs' => count(array_unique(array_column($m['entradas'], 1))), 'fecha' => $m['cargado'] ?? ''];
        },
        'meta' => $meta(true),
    ]);

    wp_register_ability('enlaces-iluminados/marcar-posts', [
        'label'       => 'Marcar posts existentes',
        'description' => 'Aplica el mapa de entidades a posts ya existentes, directo en el servidor (sin reenviar contenido). Por defecto es una PRUEBA (dry_run true): informa qué marcaría. Para aplicar, repetir con dry_run false. Elegir ids, category o all true. Respeta _ei_no_marcar.',
        'category'    => 'enlaces-iluminados',
        'input_schema' => [
            'type' => 'object',
            'properties' => [
                'ids'      => ['type' => 'array', 'items' => ['type' => 'integer']],
                'category' => ['type' => 'integer'],
                'all'      => ['type' => 'boolean', 'default' => false],
                'dry_run'  => ['type' => 'boolean', 'default' => true],
                'detalle'  => ['type' => 'boolean', 'default' => true, 'description' => 'Incluir la lista de marcas de cada post.'],
                'limit'    => ['type' => 'integer', 'default' => 200, 'minimum' => 1, 'maximum' => 500],
                'offset'   => ['type' => 'integer', 'default' => 0, 'minimum' => 0],
            ],
        ],
        'output_schema' => ['type' => 'object'],
        'permission_callback' => $pode,
        'execute_callback' => function ($in = []) {
            $in = (array) $in;
            if (!ei_mapa()) return new WP_Error('ei_mapa', 'No hay mapa cargado (usar cargar-mapa).');
            $q = ['post_type' => 'post', 'post_status' => ['publish', 'future'], 'posts_per_page' => (int) ($in['limit'] ?? 200),
                  'offset' => (int) ($in['offset'] ?? 0), 'orderby' => 'ID', 'order' => 'ASC', 'fields' => 'ids', 'no_found_rows' => false];
            if (!empty($in['ids'])) {
                $q['post__in'] = array_map('intval', $in['ids']);
            } elseif (!empty($in['category'])) {
                $q['cat'] = (int) $in['category'];
            } elseif (empty($in['all'])) {
                return new WP_Error('ei_filtro', 'Indicar ids, category o all true.');
            }
            $wq = new WP_Query($q);
            $seco = !isset($in['dry_run']) || $in['dry_run'];
            $detalle = !isset($in['detalle']) || $in['detalle'];
            global $wpdb;
            $res = [];
            $cambiados = 0;
            $total = 0;
            foreach ($wq->posts as $id) {
                if (get_post_meta($id, '_ei_no_marcar', true)) continue;
                $p = get_post($id);
                list($novo, $marcas) = ei_marcar($p->post_content, $p->post_name);
                if (!$marcas) continue;
                $cambiados++;
                $total += count($marcas);
                $item = ['id' => $id, 'titulo' => $p->post_title, 'nuevas' => count($marcas)];
                if ($detalle) $item['marcas'] = array_map(function ($m) { return $m[0] . ' → ' . $m[1]; }, $marcas);
                $res[] = $item;
                if (!$seco) {
                    $wpdb->update($wpdb->posts, ['post_content' => $novo], ['ID' => $id]);
                    clean_post_cache($id);
                    ei_agendar([], [$id]); // completa los <a href> hacia posts ya publicados
                }
            }
            return ['dry_run' => $seco, 'revisados' => count($wq->posts), 'total_filtro' => (int) $wq->found_posts,
                    'cambiados' => $cambiados, 'marcas' => $total, 'posts' => $res];
        },
        'meta' => $meta(false),
    ]);
});

/* Protege o índice do wpautop: antes dele (prioridade 9) troca o bloco por um marcador
   de bloco; depois dos shortcodes (12) devolve o HTML gravado. Sem parágrafos vazios. */
$GLOBALS['ei_reservados'] = [];
add_filter('the_content', function ($c) {
    if (strpos($c, '[' . EI_TAG) === false) return $c;
    $regex = get_shortcode_regex([EI_TAG]);
    return preg_replace_callback("/$regex/s", function ($m) {
        if ($m[1] === '[' && $m[6] === ']') return $m[0];
        $i = count($GLOBALS['ei_reservados']);
        $GLOBALS['ei_reservados'][$i] = (string) $m[5];
        return "\n<div class=\"ei-reservado-$i\"></div>\n";
    }, $c);
}, 9);
add_filter('the_content', function ($c) {
    foreach ($GLOBALS['ei_reservados'] as $i => $html) {
        $c = str_replace("<div class=\"ei-reservado-$i\"></div>", $html, $c);
    }
    $GLOBALS['ei_reservados'] = [];
    return $c;
}, 12);

/* CSS só nas páginas que usam o shortcode. */
add_action('wp_head', function () {
    if (!is_singular()) return;
    $c = (string) get_post_field('post_content', get_queried_object_id());
    if (strpos($c, '[' . EI_TAG) === false) return;
    echo '<style>
.ei-indice{margin:16px 0 28px}
.ei-resumo{background:#fdf8ec;border:1px solid #d4b26a;border-radius:8px;padding:12px 16px}
.ei-grupo{font-weight:700;margin:18px 0 8px}
.ei-grade{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(46px,1fr));gap:6px}
.ei-grade li{margin:0;padding:0}
.ei-grade a,.ei-grade span{display:block;text-align:center;padding:9px 0;border-radius:6px;font-weight:600;text-decoration:none}
.ei-indice .ei-grade li a,.ei-indice .ei-grade li span{display:block !important;width:auto !important;font-size:inherit !important;line-height:1.5 !important}
.ei-indice .ei-grade a{background:var(--ei-cor);color:#fff !important}
.ei-indice .ei-grade a:hover{filter:brightness(.85);color:#fff !important}
.ei-grade span{background:#f1f1f1;color:#aaa}
</style>';
});
