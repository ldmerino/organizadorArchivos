"""
Estilos minimalistas y monocromáticos para el procesador de PDFs
"""

class UIStyles:
    """Estilos CSS centralizados – look moderno y simple"""

    # Paleta para tema oscuro - consistente con la ventana principal
    COLORS = {
        "accent":     "#4299e1",  # azul claro que funciona en tema oscuro
        "accent_dk":  "#3182ce",  # hover/active más oscuro
        "bg":         "#1a202c",  # fondo principal oscuro
        "bg_subtle":  "#2d3748",  # fondo secundario
        "text":       "#e2e8f0",  # texto claro
        "muted":      "#a0aec0",  # texto secundario
        "border":     "#4a5568",  # bordes
        "border_dk":  "#2d3748",  # bordes más oscuros
        "success":    "#48bb78",  # verde que funciona en oscuro
        "success_bg": "#2d5a42",  # fondo verde oscuro para éxito
        "danger":     "#f56565",  # rojo que funciona en oscuro
        "danger_bg":  "#5a2d2d",  # fondo rojo oscuro para error
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
        # Tabs con mejor visibilidad de la pestaña activa
        return f"""
            QTabWidget::pane {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                background: {cls.COLORS['bg']};
                top: -1px;
            }}
            QTabBar::tab {{
                padding: 12px 20px;
                margin: 0 2px;
                border: 1px solid transparent;
                border-bottom: none;
                color: {cls.COLORS['muted']};
                background: {cls.COLORS['bg_subtle']};
                border-top-left-radius: {cls.RADIUS}px;
                border-top-right-radius: {cls.RADIUS}px;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                color: {cls.COLORS['text']};
                background: {cls.COLORS['bg']};
                border: 1px solid {cls.COLORS['border']};
                border-bottom: 1px solid {cls.COLORS['bg']};
                font-weight: 600;
            }}
            QTabBar::tab:hover:!selected {{
                color: {cls.COLORS['text']};
                background: {cls.COLORS['border']};
            }}
        """
    
    @classmethod
    def get_label_style(cls) -> str:
        return f"""
            QLabel {{
                color: {cls.COLORS['text']};
                font-size: 13px;
                font-weight: 500;
                padding: 2px 0;
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
                border: 1px solid {base};
                border-radius: {cls.RADIUS}px;
                padding: 10px 18px;
                font-weight: 600;
                min-width: 120px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {hover};
                border-color: {hover};
            }}
            QPushButton:pressed {{
                background: {hover};
                border-color: {hover};
            }}
            QPushButton:disabled {{
                background: {cls.COLORS['border_dk']};
                border-color: {cls.COLORS['border_dk']};
                color: {cls.COLORS['muted']};
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
                border: 1px solid {base};
                border-radius: {cls.RADIUS}px;
                padding: 10px 16px;
                font-weight: 600;
                min-width: 100px;
                font-size: 13px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background: {hover};
                border-color: {hover};
            }}
            QPushButton:pressed {{
                background: {hover};
                border-color: {hover};
            }}
            QPushButton:disabled {{
                background: {cls.COLORS['border_dk']};
                border-color: {cls.COLORS['border_dk']};
                color: {cls.COLORS['muted']};
            }}
        """

    @classmethod
    def get_group_style(cls, color: str = None) -> str:
        # Marco limpio y consistente
        accent = color or cls.COLORS["accent"]
        return f"""
            QGroupBox {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                margin-top: 15px;
                padding-top: 20px;
                background: {cls.COLORS['bg']};
                font-size: 13px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                top: 6px;
                padding: 4px 8px;
                color: {accent};
                background: {cls.COLORS['bg']};
                font-weight: 600;
                font-size: 14px;
                border: 1px solid {cls.COLORS['border']};
                border-radius: 4px;
            }}
        """

    @classmethod
    def get_input_style(cls) -> str:
        return f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                background: {cls.COLORS['bg_subtle']};
                font-size: 13px;
                color: {cls.COLORS['text']};
                selection-background-color: {cls.COLORS['accent']};
                selection-color: white;
            }}
            QLineEdit:focus {{
                border: 1px solid {cls.COLORS['accent']};
                background: {cls.COLORS['bg_subtle']};
                outline: none;
            }}
            QLineEdit:hover {{
                border: 1px solid {cls.COLORS['accent']};
                background: {cls.COLORS['bg_subtle']};
            }}
        """

    @classmethod
    def get_combobox_style(cls) -> str:
        return f"""
            QComboBox {{
                padding: 10px 14px;
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                background: {cls.COLORS['bg_subtle']};
                font-size: 13px;
                color: {cls.COLORS['text']};
                min-height: 22px;
            }}
            QComboBox:focus {{
                border: 1px solid {cls.COLORS['accent']};
                outline: none;
            }}
            QComboBox:hover {{
                border: 1px solid {cls.COLORS['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-style: solid;
                border-width: 6px 5px 0 5px;
                border-color: {cls.COLORS['muted']} transparent transparent transparent;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {cls.COLORS['border']};
                background: {cls.COLORS['bg_subtle']};
                color: {cls.COLORS['text']};
                selection-background-color: {cls.COLORS['accent']};
                selection-color: white;
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
                color: {cls.COLORS['text']};
            }}
        """
    
    @classmethod
    def get_table_style(cls) -> str:
        return f"""
            QTableWidget {{
                background: {cls.COLORS['bg']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.RADIUS}px;
                gridline-color: {cls.COLORS['border']};
                selection-background-color: {cls.COLORS['accent']};
                selection-color: white;
                font-size: 13px;
                color: {cls.COLORS['text']};
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border: none;
                color: {cls.COLORS['text']};
            }}
            QTableWidget::item:selected {{
                background-color: {cls.COLORS['accent']};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {cls.COLORS['bg_subtle']};
                color: {cls.COLORS['text']};
                padding: 10px 12px;
                border: 1px solid {cls.COLORS['border']};
                font-weight: 600;
                font-size: 13px;
            }}
            QHeaderView::section:hover {{
                background-color: {cls.COLORS['accent']};
                color: white;
            }}
        """