<?php
/**
 * Plugin Name: Categorías (abilities MCP)
 * Description: Abilities para crear y editar categorías de posts con su SEO de Rank Math, para el conector MCP de Claude. Misma interfaz que juegaletras/crear-categoria y juegaletras/editar-categoria.
 * Version: 1.0.0
 * Author: Daniel
 */

if (!defined('ABSPATH')) exit;

add_action('wp_abilities_api_categories_init', function () {
    if (function_exists('wp_register_ability_category')) {
        wp_register_ability_category('categorias', [
            'label'       => 'Categorías',
            'description' => 'Crear y editar categorías de posts con su SEO.',
        ]);
    }
});

/** Escribe el SEO de Rank Math enviado. Cadena vacía = borrar. */
function cat_abil_seo($term_id, $in) {
    $campos = ['seo_title' => 'rank_math_title', 'seo_description' => 'rank_math_description', 'focus_keyword' => 'rank_math_focus_keyword'];
    foreach ($campos as $k => $meta) {
        if (!array_key_exists($k, $in)) continue;
        $v = sanitize_text_field((string) $in[$k]);
        if ($v === '') delete_term_meta($term_id, $meta);
        else update_term_meta($term_id, $meta, $v);
    }
}

function cat_abil_salida($term_id) {
    $t = get_term($term_id, 'category');
    if (!$t || is_wp_error($t)) return new WP_Error('cat_no', 'La categoría no existe.');
    return [
        'id'              => (int) $t->term_id,
        'name'            => $t->name,
        'slug'            => $t->slug,
        'parent'          => (int) $t->parent,
        'description'     => $t->description,
        'count'           => (int) $t->count,
        'link'            => get_term_link($t),
        'seo_title'       => (string) get_term_meta($t->term_id, 'rank_math_title', true),
        'seo_description' => (string) get_term_meta($t->term_id, 'rank_math_description', true),
        'focus_keyword'   => (string) get_term_meta($t->term_id, 'rank_math_focus_keyword', true),
    ];
}

function cat_abil_props($con_id) {
    $p = [];
    if ($con_id) $p['id'] = ['type' => 'integer', 'description' => 'ID de la categoría a editar.'];
    $p += [
        'name'            => ['type' => 'string', 'description' => $con_id ? 'Nombre nuevo.' : 'Nombre de la categoría.'],
        'slug'            => ['type' => 'string', 'description' => 'Slug (parte de la URL del archivo de la categoría). Si ya lo usa otra categoría, da error.'],
        'parent'          => ['type' => 'integer', 'minimum' => 0, 'description' => 'ID de la categoría madre. 0 = sin madre.'],
        'description'     => ['type' => 'string', 'description' => 'Descripción de la categoría. Admite HTML simple; el tema la muestra en el archivo.'],
        'seo_title'       => ['type' => 'string', 'description' => 'Título SEO (Rank Math). Cadena vacía = borrarlo.'],
        'seo_description' => ['type' => 'string', 'description' => 'Meta description (Rank Math, ideal 140-160 caracteres). Cadena vacía = borrarla.'],
        'focus_keyword'   => ['type' => 'string', 'description' => 'Palabra clave principal (Rank Math). Cadena vacía = borrarla.'],
    ];
    return $p;
}

add_action('wp_abilities_api_init', function () {
    if (!function_exists('wp_register_ability')) return;
    $meta = [
        'annotations'  => ['readonly' => false, 'destructive' => false, 'idempotent' => false],
        'show_in_rest' => true,
        'public'       => true,
        'mcp'          => ['public' => true],
    ];
    $pode = function () { return current_user_can('manage_categories'); };

    wp_register_ability('categorias/crear-categoria', [
        'label'       => 'Crear una categoría',
        'description' => 'Crea una categoría de posts con nombre, slug, categoría madre, descripción y SEO de Rank Math (título, meta description y palabra clave). Si el nombre o el slug ya existen, da error en lugar de duplicarla. Devuelve la categoría creada.',
        'category'    => 'categorias',
        'input_schema'  => ['type' => 'object', 'properties' => cat_abil_props(false), 'required' => ['name']],
        'output_schema' => ['type' => 'object'],
        'permission_callback' => $pode,
        'execute_callback' => function ($in = []) {
            $in = (array) $in;
            $name = trim((string) ($in['name'] ?? ''));
            if ($name === '') return new WP_Error('cat_nombre', 'Falta el nombre.');
            $parent = (int) ($in['parent'] ?? 0);
            if ($parent && !term_exists($parent, 'category')) return new WP_Error('cat_madre', 'La categoría madre no existe.');
            if (term_exists($name, 'category', $parent)) return new WP_Error('cat_dup', 'Ya existe una categoría con ese nombre.');
            $args = ['parent' => $parent];
            if (isset($in['slug']) && $in['slug'] !== '') {
                $slug = sanitize_title((string) $in['slug']);
                if (get_term_by('slug', $slug, 'category')) return new WP_Error('cat_slug', 'Ese slug ya lo usa otra categoría.');
                $args['slug'] = $slug;
            }
            if (isset($in['description'])) $args['description'] = wp_kses_post((string) $in['description']);
            $r = wp_insert_term($name, 'category', $args);
            if (is_wp_error($r)) return $r;
            cat_abil_seo($r['term_id'], $in);
            return cat_abil_salida($r['term_id']);
        },
        'meta' => $meta,
    ]);

    wp_register_ability('categorias/editar-categoria', [
        'label'       => 'Editar una categoría',
        'description' => 'Cambia el nombre, el slug, la categoría madre, la descripción y/o el SEO de Rank Math (título, meta description y palabra clave) de una categoría existente, incluida la categoría por defecto. Solo cambia los campos enviados. Cambiar el slug cambia la URL del archivo de la categoría. Devuelve la categoría como quedó.',
        'category'    => 'categorias',
        'input_schema'  => ['type' => 'object', 'properties' => cat_abil_props(true), 'required' => ['id']],
        'output_schema' => ['type' => 'object'],
        'permission_callback' => $pode,
        'execute_callback' => function ($in = []) {
            $in = (array) $in;
            $id = (int) ($in['id'] ?? 0);
            $t = get_term($id, 'category');
            if (!$t || is_wp_error($t)) return new WP_Error('cat_no', 'La categoría no existe.');
            $args = [];
            if (isset($in['name']) && trim((string) $in['name']) !== '') $args['name'] = trim((string) $in['name']);
            if (isset($in['slug']) && $in['slug'] !== '') {
                $slug = sanitize_title((string) $in['slug']);
                $otra = get_term_by('slug', $slug, 'category');
                if ($otra && (int) $otra->term_id !== $id) return new WP_Error('cat_slug', 'Ese slug ya lo usa otra categoría.');
                $args['slug'] = $slug;
            }
            if (array_key_exists('parent', $in)) {
                $p = (int) $in['parent'];
                if ($p === $id) return new WP_Error('cat_madre', 'Una categoría no puede ser su propia madre.');
                if ($p && !term_exists($p, 'category')) return new WP_Error('cat_madre', 'La categoría madre no existe.');
                if ($p && in_array($id, get_ancestors($p, 'category'), true)) return new WP_Error('cat_madre', 'La madre elegida es descendiente de esta categoría.');
                $args['parent'] = $p;
            }
            if (array_key_exists('description', $in)) $args['description'] = wp_kses_post((string) $in['description']);
            if ($args) {
                $r = wp_update_term($id, 'category', $args);
                if (is_wp_error($r)) return $r;
            }
            cat_abil_seo($id, $in);
            return cat_abil_salida($id);
        },
        'meta' => $meta,
    ]);
});
