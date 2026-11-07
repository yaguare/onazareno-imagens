<?php
/**
 * Plugin Name: O Nazareno - Índice dos Salmos (fixo)
 * Description: Quando um post salmo-N da categoria Salmos é publicado (ou deixa de estar publicado), reescreve o índice 1-150 dentro do conteúdo da página livro-de-salmos. Os links ficam gravados na página.
 */
if (!defined('ABSPATH')) exit;

const ONS_SALMOS_CAT    = 50;
const ONS_SALMOS_PAGINA = 'livro-de-salmos';
const ONS_INI = '<!--indice-salmos-inicio-->';
const ONS_FIM = '<!--indice-salmos-fim-->';

function ons_salmos_html() {
    $ids = get_posts([
        'post_type'        => 'post',
        'post_status'      => 'publish',
        'cat'              => ONS_SALMOS_CAT,
        'numberposts'      => -1,
        'fields'           => 'ids',
        'suppress_filters' => true,
    ]);
    $map = [];
    foreach ($ids as $id) {
        if (preg_match('/^salmo-(\d{1,3})$/', get_post_field('post_name', $id), $m)) {
            $map[(int) $m[1]] = get_permalink($id);
        }
    }
    $livros = [[1, 41, 'Livro I'], [42, 72, 'Livro II'], [73, 89, 'Livro III'], [90, 106, 'Livro IV'], [107, 150, 'Livro V']];
    $out  = '<div class="ons-indice">';
    $out .= '<p class="ons-cont"><strong>' . count($map) . ' de 150</strong> salmos já estudados. Toque em um número em destaque para abrir o estudo; os demais estão a caminho.</p>';
    foreach ($livros as $l) {
        $out .= '<p class="ons-livro">' . $l[2] . ' <span>(Salmos ' . $l[0] . ' a ' . $l[1] . ')</span></p><ul class="ons-grid">';
        for ($n = $l[0]; $n <= $l[1]; $n++) {
            $out .= isset($map[$n])
                ? '<li><a href="' . esc_url($map[$n]) . '" title="Salmo ' . $n . '">' . $n . '</a></li>'
                : '<li><span title="Em breve">' . $n . '</span></li>';
        }
        $out .= '</ul>';
    }
    return $out . '</div>';
}

function ons_salmos_reescrever() {
    $pagina = get_page_by_path(ONS_SALMOS_PAGINA, OBJECT, 'page');
    if (!$pagina) return false;
    $bloco    = ONS_INI . ons_salmos_html() . ONS_FIM;
    $conteudo = $pagina->post_content;
    $ini = strpos($conteudo, ONS_INI);
    $fim = strpos($conteudo, ONS_FIM);
    if ($ini !== false && $fim !== false && $fim > $ini) {
        $novo = substr($conteudo, 0, $ini) . $bloco . substr($conteudo, $fim + strlen(ONS_FIM));
    } elseif (strpos($conteudo, '[indice_salmos]') !== false) {
        $novo = str_replace('[indice_salmos]', $bloco, $conteudo);
    } else {
        return false;
    }
    if ($novo === $conteudo) return true;
    // Grava direto no banco: sem revisões e sem o filtro kses (o cron não tem usuário e apagaria o JSON-LD).
    global $wpdb;
    $wpdb->update($wpdb->posts, ['post_content' => $novo], ['ID' => $pagina->ID]);
    clean_post_cache($pagina->ID);
    return true;
}

// Publicação (manual ou agendada) e despublicação de um salmo.
add_action('transition_post_status', function ($novo, $antigo, $post) {
    if ($post->post_type !== 'post' || $novo === $antigo) return;
    if ($novo !== 'publish' && $antigo !== 'publish') return;
    if (!preg_match('/^salmo-\d{1,3}$/', $post->post_name) && !has_category(ONS_SALMOS_CAT, $post)) return;
    add_action('shutdown', 'ons_salmos_reescrever');
}, 10, 3);

// Mudança de slug ou de categoria num salmo já publicado.
add_action('post_updated', function ($id, $depois, $antes) {
    if ($depois->post_type !== 'post' || $depois->post_status !== 'publish') return;
    if ($depois->post_name !== $antes->post_name || preg_match('/^salmo-\d{1,3}$/', $depois->post_name)) {
        add_action('shutdown', 'ons_salmos_reescrever');
    }
}, 10, 3);

// Primeira montagem: roda uma única vez depois de instalar.
add_action('init', function () {
    if (get_option('ons_indice_salmos_fixo') === '1') return;
    if (ons_salmos_reescrever()) update_option('ons_indice_salmos_fixo', '1');
}, 99);

add_action('wp_head', function () {
    if (!is_page(ONS_SALMOS_PAGINA)) return;
    echo '<style>
.ons-indice{margin:16px 0 28px}
.ons-cont{background:#fdf8ec;border:1px solid #d4b26a;border-radius:8px;padding:12px 16px}
.ons-livro{font-weight:700;margin:18px 0 8px}.ons-livro span{font-weight:400;color:#666}
.ons-grid{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(46px,1fr));gap:6px}
.ons-grid li{margin:0}
.ons-grid a,.ons-grid span{display:block;text-align:center;padding:9px 0;border-radius:6px;font-weight:600;text-decoration:none}
.ons-indice .ons-grid a{background:#b8913a;color:#fff !important}.ons-indice .ons-grid a:hover{background:#8f6e27;color:#fff !important}
.ons-grid span{background:#f1f1f1;color:#aaa}
</style>';
});
