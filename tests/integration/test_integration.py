from pathlib import Path
from typing import TYPE_CHECKING

# code imports
from recnys.build import build_render_tasks, build_sync_tasks
from recnys.load import load_config, load_variables
from recnys.render.renderer import TemplateRenderer
from recnys.sync.syncer import FileSyncer

# testing imports
from recnys.testing.build.arrange import make_sync_tasks
from recnys.testing.canonicalize.arrange import make_canonical_config, make_canonicalizer
from recnys.testing.load.arrange import create_config_file, create_variables_file
from recnys.testing.render.arrange import make_render_record
from recnys.testing.render.constants import TEMPLATE_FILE_CONTENT
from recnys.testing.sync.arrange import make_sync_record
from recnys.testing.sync.asserting import assert_synced_correctly
from recnys.testing.sync.constants import NORMAL_FILE_CONTENT

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


def test_integration(system: str, filesystem: FakeFilesystem) -> None:
    config_path = create_config_file(filesystem=filesystem)
    variables_path = create_variables_file(filesystem=filesystem)
    for key in make_canonical_config(system=system):
        content = TEMPLATE_FILE_CONTENT if key.endswith(".template") else NORMAL_FILE_CONTENT
        filesystem.create_file(Path.cwd() / key, contents=content)

    config = load_config(file_path=config_path)

    canonicalizer = make_canonicalizer()
    canonical_config = canonicalizer.canonicalize(loaded_config=config)

    render_tasks = build_render_tasks(config=canonical_config)
    render_record = make_render_record()
    variables = load_variables(file_path=variables_path)
    renderer = TemplateRenderer(variables=variables)
    renderer.render(tasks=render_tasks, last_record=render_record)

    sync_tasks = build_sync_tasks(config=canonical_config)
    sync_record = make_sync_record()
    syncer = FileSyncer(force=True)
    syncer.sync(tasks=sync_tasks, last_record=sync_record)

    assert_synced_correctly(tasks=make_sync_tasks(system=system))
