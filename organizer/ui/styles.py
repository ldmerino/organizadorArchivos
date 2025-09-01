"""
Estilos minimalistas y monocromáticos para el procesador de PDFs
"""

class UIStyles:
    """Estilos CSS centralizados – look moderno y simple"""

    # Paleta monocromática
    COLORS = {
        "accent":    "#3B82F6",  # azul único de la marca
        "accent_dk": "#2867D6",  # hover/active
        "bg":        "#FFFFFF",
        "bg_subtle": "#F6F7F9",
        "text":      "#1F2937",
        "muted":     "#6B7280",
        "border":    "#E5E7EB",
        "border_dk": "#D1D5DB",
        "success":   "#16A34A",  # solo para estados (no UI cromática)
        "danger":    "#DC2626",
    }

    RADIUS = 6

    @classmethod
    def get_title_style(cls) -> str:
        return f"""
            QLabel {{
                color: {cls.COLORS['text']};
                background: {cls.COLORS['bg']};
                padding: 8px 0;
                font-weight: 600;
            }}
        """

    @classmethod
    def get_tab_style(cls) -> str:
        # Tabs minimalistas con subrayado en la activa
        return f"""
            QTabWidget::pane {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                background: {cls.COLORS['bg']};
            }}
            QTabBar::tab {{
                padding: 10px 14px;
                margin: 0 6px;
                border: none;
                color: {cls.COLORS['muted']};
                background: transparent;
            }}
            QTabBar::tab:selected {{
                color: {cls.COLORS['text']};
                border-bottom: 2px solid {cls.COLORS['accent']};
            }}
            QTabBar::tab:hover {{
                color: {cls.COLORS['text']};
            }}
        """

    @classmethod
    def get_progress_style(cls) -> str:
        return f"""
            QProgressBar {{
                height: 20px;
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                background: {cls.COLORS['bg_subtle']};
                text-align: center;
                font-weight: 600;
            }}
            QProgressBar::chunk {{
                background: {cls.COLORS['accent']};
                border-radius: {cls.RADIUS - 1}px;
            }}
        """

    @classmethod
    def get_status_style(cls) -> str:
        return f"""
            QLabel {{
                padding: 10px 12px;
                background: {cls.COLORS['bg_subtle']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                font-size: 13px;
                color: {cls.COLORS['text']};
            }}
        """

    @classmethod
    def get_button_style(cls, color: str = None) -> str:
        # Un único estilo principal; usa accent por defecto
        base = color or cls.COLORS["accent"]
        hover = cls.COLORS["accent_dk"]
        return f"""
            QPushButton {{
                background: {base};
                color: white;
                border: none;
                border-radius: {cls.RADIUS}px;
                padding: 10px 18px;
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
            QPushButton:pressed {{
                background: {hover};
                opacity: 0.95;
            }}
            QPushButton:disabled {{
                background: {cls.COLORS['border_dk']};
                color: #9CA3AF;
            }}
        """

    @classmethod
    def get_small_button_style(cls, color: str = None) -> str:
        base = color or cls.COLORS["accent"]
        hover = cls.COLORS["accent_dk"]
        return f"""
            QPushButton {{
                background: {base};
                color: white;
                border: none;
                border-radius: {cls.RADIUS - 2}px;
                padding: 8px 12px;
                font-weight: 600;
                min-width: 84px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: {hover}; }}
        """

    @classmethod
    def get_group_style(cls, color: str = None) -> str:
        # Marco limpio; el color del título usa el acento
        accent = color or cls.COLORS["accent"]
        return f"""
            QGroupBox {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                margin-top: 12px;
                padding-top: 18px;
                background: {cls.COLORS['bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                top: 4px;
                padding: 0 6px;
                color: {accent};
                background: {cls.COLORS['bg']};
                font-weight: 600;
            }}
        """

    @classmethod
    def get_input_style(cls) -> str:
        return f"""
            QLineEdit {{
                padding: 9px 12px;
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS - 1}px;
                background: {cls.COLORS['bg']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {cls.COLORS['accent']};
                background: {cls.COLORS['bg']};
            }}
        """

    @classmethod
    def get_combobox_style(cls) -> str:
        return f"""
            QComboBox {{
                padding: 9px 12px;
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS - 1}px;
                background: {cls.COLORS['bg']};
                font-size: 13px;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border: 1px solid {cls.COLORS['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 26px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-style: solid;
                border-width: 5px 4px 0 4px;
                border-color: {cls.COLORS['muted']} transparent transparent transparent;
            }}
        """

    @classmethod
    def get_checkbox_style(cls) -> str:
        return f"""
            QCheckBox {{
                font-size: 13px;
                padding: 6px 2px;
                color: {cls.COLORS['text']};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {cls.COLORS['border_dk']};
                border-radius: 3px;
                background: {cls.COLORS['bg']};
            }}
            QCheckBox::indicator:checked {{
                background: {cls.COLORS['accent']};
                border-color: {cls.COLORS['accent']};
            }}
        """

    @classmethod
    def get_textedit_style(cls) -> str:
        return f"""
            QTextEdit {{
                background: {cls.COLORS['bg_subtle']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                padding: 12px;
                font-family: 'Consolas','Monaco',monospace;
                font-size: 12px;
                line-height: 1.4;
            }}
        """
