"""Vehicle selection view
展示地圖、推薦車型與確認動作"""
import flet as ft
import flet_map as map
import logging
from typing import TYPE_CHECKING

from config import USER_DASHBOARD_MAP_TEMPLATE, WINDOW_WIDTH
from constants import COLOR_BG_LIGHT_TAN, COLOR_BRAND_YELLOW, COLOR_TEXT_DARK
from views.common.navigator import build_bottom_nav_bar
from views.common.assistant import build_ai_fab
from services.map_service import MapService

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


def build_vehicle_selection_view(app_instance: "App") -> ft.View:
    logger.info("建置車型選擇 View")
    controller = app_instance.vehicle_selection_controller
    main_container = ft.Container(expand=True)

    def _build_empty_state() -> ft.Control:
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.DIRECTIONS_CAR, size=72, color=ft.Colors.GREY_400),
                ft.Text("尚未有預約資料，請回到即時預約。", color=COLOR_TEXT_DARK, size=16),
                ft.ElevatedButton(
                    text="返回即時預約",
                    icon=ft.Icons.ARROW_BACK,
                    bgcolor=COLOR_BRAND_YELLOW,
                    color=COLOR_TEXT_DARK,
                    on_click=lambda _: app_instance.page.go("/app/user/instant_booking"),
                ),
            ],
        )

    def _build_map_section():
        map_ctx = controller.get_map_context()
        if not map_ctx:
            return ft.Container(expand=2, content=_build_empty_state())

        pickup_marker = MapService.create_marker(
            icon=ft.Icons.MY_LOCATION,
            color=ft.Colors.GREEN_700,
            coordinates=(map_ctx["pickup"]["lat"], map_ctx["pickup"]["lon"]),
        )
        dropoff_marker = MapService.create_marker(
            icon=ft.Icons.FLAG,
            color=ft.Colors.RED_600,
            coordinates=(map_ctx["dropoff"]["lat"], map_ctx["dropoff"]["lon"]),
        )
        polyline = MapService.create_polyline(
            map_ctx["polyline"],
            color=ft.Colors.BLUE_600,
            width=5,
        )
        map_control = map.Map(
            expand=True,
            initial_center=map.MapLatitudeLongitude(*map_ctx["center"]),
            initial_zoom=map_ctx["zoom"],
            interaction_configuration=map.MapInteractionConfiguration(
                flags=map.MapInteractiveFlag.NONE
            ),
            layers=[
                map.TileLayer(url_template=USER_DASHBOARD_MAP_TEMPLATE),
                map.PolylineLayer(polylines=[polyline]),
                map.MarkerLayer(markers=[pickup_marker, dropoff_marker]),
            ],
        )
        summary = controller.get_trip_summary()
        overlay = ft.Container(
            width=WINDOW_WIDTH * 0.9,
            height=80,
            padding=10,
            margin=10,
            bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
            border_radius=10,
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Text(
                        f"{summary.get('pickup', '')} → {summary.get('dropoff', '')}",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXT_DARK,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        f"約 {summary.get('distance_km', 0)} 公里 · {summary.get('eta_min', 10)} 分鐘",
                        size=11,
                        color=ft.Colors.GREY_700,
                    ),
                ],
            ),
        )
        return ft.Container(
            expand=2,
            content=ft.Stack(controls=[map_control, overlay]),
        )

    def _build_vehicle_card(option: dict) -> ft.Control:
        border_color = ft.Colors.GREEN_700 if option["is_selected"] else ft.Colors.GREY_300
        badge_controls = []
        if option["is_recommended"]:
            badge_controls.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    bgcolor=ft.Colors.GREEN_100,
                    border_radius=20,
                    content=ft.Text("推薦", size=12, color=ft.Colors.GREEN_800),
                )
            )
        if option["is_selected"]:
            badge_controls.append(
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=ft.Colors.GREEN_700)
            )
        return ft.Container(
            on_click=lambda _: controller.select_vehicle(option["type"]),
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(2, border_color),
            border_radius=10,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(option["icon"], size=22, color=COLOR_TEXT_DARK),
                                    ft.Column(
                                        spacing=0,
                                        controls=[
                                            ft.Text(option["label"], size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                                            ft.Text(option["description"], size=11, color=ft.Colors.GREY_600),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Row(spacing=4, controls=badge_controls),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(option["eta"], size=11, color=ft.Colors.GREY_600),
                            ft.Text(option["price"], size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                        ],
                    ),
                ],
            ),
        )

    def _build_info_section():
        if not controller or not controller.trip:
            return _build_empty_state()

        summary = controller.get_trip_summary()
        vehicle_cards = [
            _build_vehicle_card(option) for option in controller.get_vehicle_options()
        ]
        luggage_text = f"{summary.get('luggage_count', 0)} 件行李"
        if summary.get("luggage_note"):
            luggage_text += f" · {summary['luggage_note']}"

        return ft.Container(
            expand=3,
            padding=20,
            bgcolor=COLOR_BG_LIGHT_TAN,
            content=ft.Column(
                expand=True,
                spacing=12,
                controls=[
                    ft.Text("選擇推薦車型", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                    # ft.Container(
                    #     padding=12,
                    #     border_radius=10,
                    #     bgcolor=ft.Colors.WHITE,
                    #     content=ft.Column(
                    #         spacing=4,
                    #         controls=[
                    #             ft.Text("行李資訊", size=10, color=ft.Colors.GREY_600),
                    #             ft.Text(luggage_text, size=12, color=COLOR_TEXT_DARK, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    #         ],
                    #     ),
                    # ),
                    ft.Column(spacing=12, controls=vehicle_cards, scroll=ft.ScrollMode.AUTO, expand=True),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.OutlinedButton(
                                text="返回",
                                icon=ft.Icons.ARROW_BACK,
                                expand=1,
                                on_click=controller.go_back_to_edit,
                            ),
                            ft.ElevatedButton(
                                text="確認派車",
                                icon=ft.Icons.DONE,
                                bgcolor=COLOR_BRAND_YELLOW,
                                color=COLOR_TEXT_DARK,
                                expand=2,
                                on_click=controller.confirm_vehicle_choice,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _compose_layout():
        if not controller:
            return _build_empty_state()
        return ft.Column(
            spacing=0,
            expand=True,
            controls=[
                _build_map_section(),
                _build_info_section(),
            ],
        )

    def update_view(self=None):
        main_container.content = _compose_layout()
        if main_container.page:
            main_container.update()
        else:
            logger.debug("Vehicle selection view 尚未掛載，略過 update()")

    if controller:
        controller.bind_view(type("VehicleSelectionViewAdapter", (), {"update_view": update_view})())

    # 初始內容不調用 update()，避免控制項尚未掛載於頁面時的錯誤
    main_container.content = _compose_layout()

    return ft.View(
        route="/app/user/vehicle_selection",
        padding=0,
        bgcolor=COLOR_BG_LIGHT_TAN,
        floating_action_button=build_ai_fab(app_instance),
        controls=[
            main_container,
            build_bottom_nav_bar(app_instance, selected_index=1),
        ],
    )
