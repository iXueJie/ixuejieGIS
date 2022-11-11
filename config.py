"""
应用程序运行环境配置，应该在程序运行一开始最先被引用
"""


def _config():
    # 局部引用，不要污染全局命名空间
    import sys
    sys.path.append('plugins')

    from plugins.processing.core.Processing import Processing
    Processing.initialize()


_config()
