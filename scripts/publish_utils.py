"""本地交付先完整复制，再切换入口；切换失败时恢复旧版。"""

from datetime import datetime
from pathlib import Path
import shutil
import tempfile


def replace_delivery(artifacts: Path, destination: Path, run: Path) -> None:
    artifacts, destination, run = (path.resolve() for path in (artifacts, destination, run))
    if run == destination or run.is_relative_to(destination):
        raise ValueError('工作目录不能位于待替换的交付目录内')
    # 暂存与入口同层，最后只做同文件系统的目录重命名。
    with tempfile.TemporaryDirectory(prefix='_publish-', dir=destination.parent) as folder:
        staging = Path(folder).resolve()
        if staging.parent != destination.parent:
            raise ValueError('发布暂存目录必须位于交付入口的父目录内')
        staged = staging / 'delivery'
        shutil.copytree(artifacts, staged)
        backup = None
        if destination.exists():
            backup = run / 'previous-deliveries' / f'{datetime.now():%Y%m%d-%H%M%S-%f}'
            if not backup.resolve().is_relative_to(run):
                raise ValueError('历史交付路径必须位于本次工作目录内')
            backup.parent.mkdir(parents=True, exist_ok=True)
            destination.rename(backup)
        try:
            staged.rename(destination)
        except OSError:
            if backup is not None:
                try:
                    backup.rename(destination)
                except OSError as error:
                    raise OSError(f'入口切换及恢复失败，旧版保留在：{backup}') from error
            raise
