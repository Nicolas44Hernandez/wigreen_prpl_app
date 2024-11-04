"""REST API Use situations controler package"""

from .rest_controller import bp, UseSituationsListApi, UseSituationsApi

bp.add_url_rule(
    "/use_situations/list", view_func=UseSituationsListApi.as_view("use_situations_list_api")
)
bp.add_url_rule("/use_situations/current", view_func=UseSituationsApi.as_view("use_situations_api"))
