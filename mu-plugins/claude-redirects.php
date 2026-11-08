<?php
/**
 * Plugin Name: Claude – redireccionamientos de Rank Math
 * Description: Habilidades del conector para listar y crear redireccionamientos 301 en Rank Math (por lote, con modo prueba).
 * Version: 1.1.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Normaliza una dirección de origen al formato que guarda Rank Math:
 * sin dominio y sin barras al principio ni al final ("quiz-sobre-davi").
 */
function claude_redir_normalize_source( $url ) {
	$url  = trim( (string) $url );
	$home = untrailingslashit( home_url() );
	if ( 0 === stripos( $url, $home ) ) {
		$url = substr( $url, strlen( $home ) );
	}
	$url = preg_replace( '#^https?://[^/]+#i', '', $url );
	$url = strtok( $url, '?#' );
	return trim( (string) $url, '/' );
}

/** Lee todos los redireccionamientos directamente de la tabla de Rank Math. */
function claude_redir_all() {
	global $wpdb;
	$table = $wpdb->prefix . 'rank_math_redirections';
	if ( $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', $table ) ) !== $table ) {
		return new WP_Error( 'sin_tabla', 'No existe la tabla de redireccionamientos de Rank Math (¿módulo Redireccionamientos desactivado?).' );
	}
	$rows = $wpdb->get_results( "SELECT id, sources, url_to, header_code, hits, status, created FROM {$table} ORDER BY id ASC", ARRAY_A );
	$out  = array();
	foreach ( (array) $rows as $r ) {
		$sources = maybe_unserialize( $r['sources'] );
		$pats    = array();
		foreach ( (array) $sources as $s ) {
			if ( is_array( $s ) && isset( $s['pattern'] ) ) {
				$pats[] = array(
					'pattern'    => $s['pattern'],
					'comparison' => isset( $s['comparison'] ) ? $s['comparison'] : 'exact',
				);
			}
		}
		$out[] = array(
			'id'          => (int) $r['id'],
			'sources'     => $pats,
			'url_to'      => $r['url_to'],
			'header_code' => (int) $r['header_code'],
			'hits'        => (int) $r['hits'],
			'status'      => $r['status'],
			'created'     => $r['created'],
		);
	}
	return $out;
}

add_action( 'wp_abilities_api_init', function () {
	if ( ! function_exists( 'wp_register_ability' ) ) {
		return;
	}

	/* ---------- Listar ---------- */
	wp_register_ability(
		'claude-wp/list-redirects',
		array(
			'label'               => 'Listar redireccionamientos',
			'description'         => 'Lista los redireccionamientos de Rank Math (origen, destino, código, visitas y estado). Se puede filtrar por texto en el origen o el destino.',
			'category'            => 'claude-contenido',
			'input_schema'        => array(
				'type'       => 'object',
				'properties' => array(
					'search' => array(
						'type'        => 'string',
						'description' => 'Texto a buscar en el origen o en el destino (opcional).',
					),
				),
			),
			'output_schema'       => array( 'type' => 'object' ),
			'execute_callback'    => function ( $input ) {
				$all = claude_redir_all();
				if ( is_wp_error( $all ) ) {
					return $all;
				}
				$q = isset( $input['search'] ) ? trim( (string) $input['search'] ) : '';
				if ( '' !== $q ) {
					$all = array_values( array_filter( $all, function ( $r ) use ( $q ) {
						if ( false !== stripos( $r['url_to'], $q ) ) {
							return true;
						}
						foreach ( $r['sources'] as $s ) {
							if ( false !== stripos( $s['pattern'], $q ) ) {
								return true;
							}
						}
						return false;
					} ) );
				}
				return array(
					'total' => count( $all ),
					'items' => $all,
				);
			},
			'permission_callback' => function ( $input ) {
				return current_user_can( 'edit_others_posts' );
			},
			'meta'                => array(
				'show_in_rest' => true,
				'annotations'  => array( 'readonly' => true ),
				'mcp'          => array( 'public' => true ),
			),
		)
	);

	/* ---------- Crear por lote ---------- */
	wp_register_ability(
		'claude-wp/create-redirects',
		array(
			'label'               => 'Crear redireccionamientos 301 en lote',
			'description'         => 'Crea redireccionamientos en Rank Math, hasta 300 por llamada. Cada item lleva "from" (dirección vieja, con o sin dominio) y "to" (dirección nueva). Código 301 por defecto. Se saltan los orígenes que ya tienen un redireccionamiento y los que apuntan a sí mismos. Por defecto es una PRUEBA (dry_run true): solo informa qué crearía. Para aplicar, repetir con dry_run false.',
			'category'            => 'claude-contenido',
			'input_schema'        => array(
				'type'       => 'object',
				'required'   => array( 'items' ),
				'properties' => array(
					'items'       => array(
						'type'     => 'array',
						'maxItems' => 300,
						'items'    => array(
							'type'       => 'object',
							'required'   => array( 'from', 'to' ),
							'properties' => array(
								'from' => array( 'type' => 'string' ),
								'to'   => array( 'type' => 'string' ),
							),
						),
					),
					'header_code' => array(
						'type'        => 'integer',
						'enum'        => array( 301, 302, 307, 410, 451 ),
						'description' => 'Código HTTP (301 por defecto).',
					),
					'dry_run'     => array(
						'type'        => 'boolean',
						'description' => 'true (por defecto) = solo prueba; false = crear.',
					),
				),
			),
			'output_schema'       => array( 'type' => 'object' ),
			'execute_callback'    => function ( $input ) {
				if ( ! class_exists( '\RankMath\Redirections\Redirection' ) ) {
					return new WP_Error( 'sin_rank_math', 'El módulo Redireccionamientos de Rank Math no está cargado: actívalo en Rank Math → Panel → Módulos.' );
				}
				$dry  = ! isset( $input['dry_run'] ) || false !== $input['dry_run'];
				$code = isset( $input['header_code'] ) ? (int) $input['header_code'] : 301;

				$existing = claude_redir_all();
				if ( is_wp_error( $existing ) ) {
					return $existing;
				}
				$taken = array();
				foreach ( $existing as $r ) {
					foreach ( $r['sources'] as $s ) {
						$taken[ strtolower( trim( $s['pattern'], '/' ) ) ] = $r['id'];
					}
				}

				$created = array();
				$skipped = array();
				$errors  = array();
				$seen    = array();

				foreach ( (array) $input['items'] as $i => $item ) {
					$from = claude_redir_normalize_source( isset( $item['from'] ) ? $item['from'] : '' );
					$to   = isset( $item['to'] ) ? trim( (string) $item['to'] ) : '';
					if ( '' === $from || '' === $to ) {
						$errors[] = array( 'index' => $i, 'error' => 'from o to vacío' );
						continue;
					}
					if ( 0 === strpos( $to, '/' ) ) {
						$to = home_url( $to );
					}
					$key = strtolower( $from );
					if ( claude_redir_normalize_source( $to ) === $from ) {
						$skipped[] = array( 'from' => $from, 'motivo' => 'el destino es igual al origen' );
						continue;
					}
					if ( isset( $taken[ $key ] ) ) {
						$skipped[] = array( 'from' => $from, 'motivo' => 'ya existe (redireccionamiento ID ' . $taken[ $key ] . ')' );
						continue;
					}
					if ( isset( $seen[ $key ] ) ) {
						$skipped[] = array( 'from' => $from, 'motivo' => 'repetido en este lote' );
						continue;
					}
					$seen[ $key ] = true;

					if ( $dry ) {
						$created[] = array( 'from' => $from, 'to' => $to, 'code' => $code );
						continue;
					}

					$redir = \RankMath\Redirections\Redirection::from(
						array(
							'sources'     => array(
								array(
									'pattern'    => $from,
									'comparison' => 'exact',
								),
							),
							'url_to'      => $to,
							'header_code' => $code,
							'status'      => 'active',
						)
					);
					$id = $redir->save();
					if ( $id ) {
						$created[]      = array( 'id' => (int) $id, 'from' => $from, 'to' => $to, 'code' => $code );
						$taken[ $key ] = (int) $id;
					} else {
						$errors[] = array( 'from' => $from, 'error' => 'Rank Math no lo guardó (¿bucle infinito o destino inválido?)' );
					}
				}

				return array(
					'dry_run'  => $dry,
					'creados'  => count( $created ),
					'saltados' => count( $skipped ),
					'errores'  => count( $errors ),
					'items'    => $created,
					'skipped'  => $skipped,
					'errors'   => $errors,
				);
			},
			'permission_callback' => function ( $input ) {
				return current_user_can( 'edit_others_posts' );
			},
			'meta'                => array(
				'show_in_rest' => true,
				'annotations'  => array( 'destructive' => false ),
				'mcp'          => array( 'public' => true ),
			),
		)
	);

	/* ---------- Corregir enlaces internos viejos ---------- */
	wp_register_ability(
		'claude-wp/fix-old-links',
		array(
			'label'               => 'Corregir enlaces internos que pasan por un redireccionamiento',
			'description'         => 'Recorre el contenido de posts, páginas y productos y cambia cada enlace interno (href) cuyo destino es el origen de un redireccionamiento de Rank Math por la dirección final, así ningún enlace del sitio pasa por un 301. Toca solo los href, no el texto. Por defecto es una PRUEBA (dry_run true): solo informa qué cambiaría. Para aplicar, repetir con dry_run false. WordPress guarda una revisión de cada post modificado.',
			'category'            => 'claude-contenido',
			'input_schema'        => array(
				'type'       => 'object',
				'properties' => array(
					'dry_run' => array( 'type' => 'boolean', 'description' => 'true (por defecto) = solo prueba; false = aplicar.' ),
					'limit'   => array( 'type' => 'integer', 'minimum' => 1, 'maximum' => 1000, 'description' => 'Máximo de posts a revisar (500 por defecto).' ),
					'offset'  => array( 'type' => 'integer', 'minimum' => 0, 'description' => 'Saltar los primeros N posts.' ),
				),
			),
			'output_schema'       => array( 'type' => 'object' ),
			'execute_callback'    => function ( $input ) {
				$dry    = ! isset( $input['dry_run'] ) || false !== $input['dry_run'];
				$limit  = isset( $input['limit'] ) ? (int) $input['limit'] : 500;
				$offset = isset( $input['offset'] ) ? (int) $input['offset'] : 0;

				$all = claude_redir_all();
				if ( is_wp_error( $all ) ) {
					return $all;
				}
				$map = array();
				foreach ( $all as $r ) {
					if ( 'active' !== $r['status'] || ! in_array( $r['header_code'], array( 301, 302, 307 ), true ) ) {
						continue;
					}
					foreach ( $r['sources'] as $s ) {
						if ( 'exact' === $s['comparison'] ) {
							$map[ strtolower( trim( $s['pattern'], '/' ) ) ] = $r['url_to'];
						}
					}
				}
				if ( ! $map ) {
					return array( 'mensaje' => 'No hay redireccionamientos exactos activos.' );
				}

				$host = preg_quote( wp_parse_url( home_url(), PHP_URL_HOST ), '#' );
				$re   = '#(href\s*=\s*["\'])((?:https?:)?//(?:www\.)?' . $host . ')?(/[^"\'\#?\s]*)([^"\']*)(["\'])#i';

				$q = new WP_Query( array(
					'post_type'      => array( 'post', 'page', 'product' ),
					'post_status'    => array( 'publish', 'future', 'draft', 'private', 'pending' ),
					'posts_per_page' => $limit,
					'offset'         => $offset,
					'orderby'        => 'ID',
					'order'          => 'ASC',
					'fields'         => 'ids',
					'no_found_rows'  => false,
				) );

				$changed = array();
				$total   = 0;
				foreach ( $q->posts as $pid ) {
					$content = get_post_field( 'post_content', $pid, 'raw' );
					$hits    = array();
					$new     = preg_replace_callback( $re, function ( $m ) use ( $map, &$hits ) {
						$key = strtolower( trim( rawurldecode( $m[3] ), '/' ) );
						if ( '' === $key || ! isset( $map[ $key ] ) ) {
							return $m[0];
						}
						$hits[] = $m[3] . ' → ' . $map[ $key ];
						return $m[1] . $map[ $key ] . $m[4] . $m[5];
					}, $content );
					if ( $hits && $new !== $content ) {
						$total += count( $hits );
						$changed[] = array(
							'id'      => $pid,
							'title'   => get_the_title( $pid ),
							'enlaces' => count( $hits ),
							'detalle' => array_slice( $hits, 0, 20 ),
						);
						if ( ! $dry ) {
							wp_update_post( array( 'ID' => $pid, 'post_content' => wp_slash( $new ) ) );
						}
					}
				}

				return array(
					'dry_run'           => $dry,
					'posts_revisados'   => count( $q->posts ),
					'posts_en_total'    => (int) $q->found_posts,
					'posts_con_cambios' => count( $changed ),
					'enlaces'           => $total,
					'items'             => $changed,
				);
			},
			'permission_callback' => function ( $input ) {
				return current_user_can( 'edit_others_posts' );
			},
			'meta'                => array(
				'show_in_rest' => true,
				'annotations'  => array( 'destructive' => false ),
				'mcp'          => array( 'public' => true ),
			),
		)
	);
} );
