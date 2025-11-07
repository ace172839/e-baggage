def build_instant_booking_content(app_instance: 'App'):
    def handle_tap(e: map.MapTapEvent):
        logger.info(f"地圖被點擊 at global_x: {e.global_x}, global_y: {e.global_y}, local_x: {e.local_x}, local_y: {e.local_y}")

    marker_layer_ref = ft.Ref[map.MarkerLayer]()
    
    return ft.Column(
        [
            map.Map(
                expand=True,
                on_init=lambda e: logger.info("地圖初始化完成"),
                initial_zoom=16,
                initial_center=map.MapLatitudeLongitude(*USER_DASHBOARD_DEFAULT_LOCATION),
                interaction_configuration=map.MapInteractionConfiguration(
                    flags=map.MapInteractiveFlag.ALL
                ),
                on_tap=handle_tap,
                on_secondary_tap=handle_tap,
                on_long_press=handle_tap,
                on_event=lambda e: logger.info(f"Map event: {e}"),
                layers=[
                    map.TileLayer(
                        url_template=USER_DASHBOARD_MAP_TEMPLATE,
                        on_image_error=lambda e: print("TileLayer Error"),
                    ),
                    # map.RichAttribution(
                    #     attributions=[
                    #         map.TextSourceAttribution(
                    #             text="OpenStreetMap Contributors",
                    #             on_click=lambda e: e.page.launch_url(
                    #                 "https://openstreetmap.org/copyright"
                    #             ),
                    #         ),
                    #         map.TextSourceAttribution(
                    #             text="Flet",
                    #             on_click=lambda e: e.page.launch_url(
                    #                 "https://flet.dev"
                    #             ),
                    #         ),
                    #     ]
                    # ),
                    # map.SimpleAttribution(
                    #     text="Flet",
                    #     alignment=ft.alignment.top_right,
                    #     on_click=lambda e: print("Clicked SimpleAttribution"),
                    # ),
                    map.MarkerLayer(
                        ref=marker_layer_ref,
                        markers=[
                            map.Marker(
                                content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED, size=35),
                                coordinates=map.MapLatitudeLongitude(25.01443, 121.4638),
                            ),
                        ],
                    ),
                    # map.CircleLayer(
                    #     ref=circle_layer_ref,
                    #     circles=[
                    #         map.CircleMarker(
                    #             radius=10,
                    #             coordinates=map.MapLatitudeLongitude(16, 24),
                    #             color=ft.Colors.RED,
                    #             border_color=ft.Colors.BLUE,
                    #             border_stroke_width=4,
                    #         ),
                    #     ],
                    # ),
                    # map.PolygonLayer(
                    #     polygons=[
                    #         map.PolygonMarker(
                    #             label="Popular Touristic Area",
                    #             label_text_style=ft.TextStyle(
                    #                 color=ft.Colors.BLACK,
                    #                 size=15,
                    #                 weight=ft.FontWeight.BOLD,
                    #             ),
                    #             color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE),
                    #             coordinates=[
                    #                 map.MapLatitudeLongitude(10, 10),
                    #                 map.MapLatitudeLongitude(30, 15),
                    #                 map.MapLatitudeLongitude(25, 45),
                    #             ],
                    #         ),
                    #     ],
                    # ),
                    # map.PolylineLayer(
                    #     polylines=[
                    #         map.PolylineMarker(
                    #             border_stroke_width=3,
                    #             border_color=ft.Colors.RED,
                    #             gradient_colors=[ft.Colors.BLACK, ft.Colors.BLACK],
                    #             color=ft.Colors.with_opacity(0.6, ft.Colors.GREEN),
                    #             coordinates=[
                    #                 map.MapLatitudeLongitude(10, 10),
                    #                 map.MapLatitudeLongitude(30, 15),
                    #                 map.MapLatitudeLongitude(25, 45),
                    #             ],
                    #         ),
                    #     ],
                    # ),
                ],
            ),
        ],
        height=400,
        expand=True,
    )