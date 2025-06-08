import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QGroupBox, QTextEdit, 
                            QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont, QPalette, QColor
from config_manager import load_config, save_config
import subprocess
import os

class DarkTheme:
    @staticmethod
    def apply(app):
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)

class MCPConfigApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("特能拉科技-小智AI联网搜索MCP服务")
        self.config = load_config()
        
        # 窗口尺寸设置（根据图片比例调整）
        self.resize(720, 580)
        self.setMinimumSize(600, 450)
        
        # 字体设置（Mac系统推荐）
        self.default_font = QFont("PingFang SC", 12)
        self.setFont(self.default_font)
        
        self.init_ui()
        
    def init_ui(self):
        # 主窗口布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # API配置区域
        config_group = QGroupBox("API配置")
        config_group.setFont(QFont("PingFang SC", 12, QFont.Bold))
        config_layout = QVBoxLayout()
        
        # MCP端点
        mcp_layout = QHBoxLayout()
        mcp_label = QLabel("MCP端点:")
        mcp_label.setFixedWidth(80)
        self.mcp_entry = QLineEdit()
        self.mcp_entry.setText(self.config.get("MCP_ENDPOINT", "http://xiaozhi.me/console/agents"))
        self.mcp_entry.setPlaceholderText("请输入MCP服务端点URL")
        mcp_layout.addWidget(mcp_label)
        mcp_layout.addWidget(self.mcp_entry)
        config_layout.addLayout(mcp_layout)
        
        # 间隔线
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setFrameShadow(QFrame.Sunken)
        config_layout.addWidget(sep1)
        
        # 智谱API密钥
        api_layout = QHBoxLayout()
        api_label = QLabel("智谱API密钥:")
        api_label.setFixedWidth(80)
        self.api_entry = QLineEdit()
        self.api_entry.setText(self.config.get("ZHIPU_API_KEY", "/usercenter/proj-mgmt/apikeysx"))
        self.api_entry.setPlaceholderText("请输入智谱AI的API密钥路径")
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_entry)
        config_layout.addLayout(api_layout)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # 按钮区域
        btn_frame = QFrame()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 10, 0, 10)
        
        self.save_btn = QPushButton("保存配置")
        self.save_btn.setFixedHeight(32)
        self.save_btn.clicked.connect(self.save_config)
        
        self.start_btn = QPushButton("启动服务")
        self.start_btn.setFixedHeight(32)
        self.start_btn.clicked.connect(self.start_service)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.start_btn)
        btn_frame.setLayout(btn_layout)
        main_layout.addWidget(btn_frame)
        
        # 操作日志区域
        log_group = QGroupBox("操作日志")
        log_group.setFont(QFont("PingFang SC", 12, QFont.Bold))
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #2A2A2A; color: #E0E0E0;")
        
        # 添加初始日志时间戳（如图片所示）
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.log_text.append(current_time)
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group, stretch=1)
        
    def save_config(self):
        self.log_action("正在保存配置...")
        new_config = {
            "MCP_ENDPOINT": self.mcp_entry.text(),
            "ZHIPU_API_KEY": self.api_entry.text()
        }
        save_config(new_config)
        QMessageBox.information(self, "保存成功", "配置已保存至系统！")
        self.log_action("配置保存成功")
        
    def start_service(self):
        try:
            self.log_action("正在启动MCP服务...")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            mcp_script = os.path.join(current_dir, "mcp_pipe.py")
            web_search_script = os.path.join(current_dir, "websearch.py")
            
            # 添加环境变量确保子进程能找到Python解释器
            env = os.environ.copy()
            env["PYTHONPATH"] = current_dir
            
            subprocess.Popen(
                ["python", mcp_script, web_search_script],
                cwd=current_dir,
                env=env
            )
            QMessageBox.information(self, "服务启动", "MCP后台服务已启动运行")
            self.log_action("服务启动成功")
        except Exception as e:
            self.log_action(f"服务启动失败: {str(e)}")
            QMessageBox.critical(self, "启动错误", f"服务启动异常:\n{str(e)}")
            
    def log_action(self, message):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.log_text.append(f"{timestamp}\n{message}\n")
        
    def closeEvent(self, event):
        """重写关闭事件确保资源释放"""
        reply = QMessageBox.question(
            self, '退出确认',
            '确定要关闭MCP配置工具吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    DarkTheme.apply(app)  # 应用深色主题
    
    
    # 设置应用图标（可选）
    # app.setWindowIcon(QIcon("icon.png"))
    
    window = MCPConfigApp()
    window.show()
    sys.exit(app.exec_())