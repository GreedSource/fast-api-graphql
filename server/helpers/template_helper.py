from datetime import datetime
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from server.config.settings import settings
from server.decorators.singleton_decorator import singleton


@singleton
class TemplateHelper:
    def init_app(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader("server/templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        # ✅ Variables globales disponibles en TODOS los templates
        self.env.globals.update(
            app_name=settings.APP_NAME,
            frontend_url=settings.FRONTEND_URL,
            company_name=getattr(settings, "COMPANY_NAME", "Mi Empresa"),
            logo_url=getattr(settings, "LOGO_URL", ""),
            now=lambda: datetime.now(),
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        template: str = self.env.get_template(template_name).render(**context)
        return template
