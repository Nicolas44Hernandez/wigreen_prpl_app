# test_use_situations_api.py
from unittest.mock import patch
from server.common.exception.code import ErrorCode


def test_get_use_situation_list(client):
    # GIVEN

    with patch(
        "server.rest_api.use_situations_controller.rest_controller.orchestrator_use_situations_service"
    ) as mock_service:
        mock_service.get_use_situation_list.return_value = ["US_1", "US_2"]

        # WHEN
        response = client.get("api/use_situations/list")

        # THEN
        assert response.status_code == 200
        assert response.json == {"use_situations": ["US_1", "US_2"]}
        mock_service.get_use_situation_list.assert_called_once()


def test_get_current_use_situation(client):
    # GIVEN
    with patch(
        "server.rest_api.use_situations_controller.rest_controller.orchestrator_use_situations_service"
    ) as mock_service:
        mock_service.get_current_use_situation.return_value = "default"

        # WHEN
        response = client.get("api/use_situations/current")

        # THEN
        assert response.status_code == 200
        assert response.json == {"use_situation": "default"}
        mock_service.get_current_use_situation.assert_called_once()


def test_post_set_current_use_situation(client):
    # GIVEN
    with patch(
        "server.rest_api.use_situations_controller.rest_controller.orchestrator_use_situations_service"
    ) as mock_service:
        new_use_situation = "NEW_USE_SITUATION"

        # WHEN
        response = client.post("api/use_situations/current?use_situation=" + new_use_situation)

        # THEN
        assert response.status_code == 200
        assert response.json == {"use_situation": new_use_situation}
        mock_service.set_use_situation.assert_called_once_with(use_situation=new_use_situation)


def test_post_set_current_use_situation_missing_arg(client):
    # GIVEN
    with patch(
        "server.rest_api.use_situations_controller.rest_controller.orchestrator_use_situations_service"
    ):
        # WHEN
        response = client.post("api/use_situations/current")

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message
