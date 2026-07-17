"""Streamlit entrypoint — thin shell delegating to navigation router."""

from app.ui.renderer.navigation import NavigationRouter, configure_streamlit


def main() -> None:
    configure_streamlit()
    NavigationRouter().run()


if __name__ == "__main__":
    main()
