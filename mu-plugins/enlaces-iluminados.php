<?php
/**
 * Plugin Name: Enlaces iluminados
 * Description: Índice de uma série de posts (1-150, capítulos, códigos...) em que cada item vira link FIXO no conteúdo da página no momento em que o post correspondente é publicado. Uso: [enlaces_iluminados slug="salmo-{n}" desde="1" hasta="150"] numa página.
 * Version: 1.2.0
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

function ei_agendar() {
    static $feito = false;
    if ($feito) return;
    $feito = true;
    add_action('shutdown', 'ei_reescrever_tudo');
}

/* Gatilhos: publicação/despublicação, troca de slug e páginas com o shortcode salvas. */
add_action('transition_post_status', function ($novo, $antigo, $post) {
    if ($novo === $antigo || in_array($post->post_type, ['revision', 'nav_menu_item'], true)) return;
    if ($novo === 'publish' || $antigo === 'publish') ei_agendar();
}, 10, 3);

add_action('post_updated', function ($id, $depois, $antes) {
    if ($depois->post_status === 'publish' && $depois->post_name !== $antes->post_name) ei_agendar();
}, 10, 3);

add_action('save_post', function ($id, $post) {
    if (wp_is_post_revision($id)) return;
    if (ei_tem_tag((string) $post->post_content)) ei_agendar();
}, 10, 2);

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
