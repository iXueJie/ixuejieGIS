"""
应用程序运行环境配置，应该在程序运行一开始最先被引用
"""


def setup_env():
    # 局部引用，不要污染全局命名空间
    import sys
    sys.path.append('plugins')

    from processing import Processing
    Processing.initialize()
