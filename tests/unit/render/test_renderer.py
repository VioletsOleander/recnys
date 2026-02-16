from typing import TYPE_CHECKING

from recnys.testing.build.arrange import make_render_tasks
from recnys.testing.render.arrange import create_source_files, make_render_record, make_renderer
from recnys.testing.render.asserting import assert_render_record_io, assert_rendered_correctly

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


def test_render(system: str, filesystem: FakeFilesystem) -> None:
    render_tasks = make_render_tasks(system=system)
    create_source_files(filesystem=filesystem, tasks=render_tasks)
    record = make_render_record()
    renderer = make_renderer()

    record = renderer.render(tasks=render_tasks, last_record=record)

    assert_rendered_correctly(tasks=render_tasks)
    assert_render_record_io(render_record=record)


def test_render_with_variables_file_change_detection(
    system: str, filesystem: FakeFilesystem
) -> None:
    """Test that changing variables.yaml triggers re-rendering of all templates."""
    from pathlib import Path
    
    from recnys.io.record import ExecutionRecord
    from recnys.io.utils import get_normalized_file_hash
    from recnys.render.renderer import TemplateRenderer
    from recnys.testing.build.arrange import make_render_tasks
    from recnys.testing.load.constants import LOADED_VARIABLES, VARIABLES_FILE_CONTENT
    from recnys.testing.render.arrange import create_source_files
    from recnys.testing.render.constants import RENDERED_CONTENT, TEMPLATE_FILE_CONTENT
    
    # Setup
    render_tasks = make_render_tasks(system=system)
    create_source_files(filesystem=filesystem, tasks=render_tasks)
    variables_file = Path.cwd() / "variables.yaml"
    filesystem.create_file(variables_file, contents=VARIABLES_FILE_CONTENT)
    
    # First render with variables file
    renderer = TemplateRenderer(
        variables=LOADED_VARIABLES, 
        variables_file_path=variables_file
    )
    record = ExecutionRecord()
    record = renderer.render(tasks=render_tasks, last_record=record)
    
    # Verify files were rendered
    assert_rendered_correctly(tasks=render_tasks)
    
    # Verify variables file hash is stored in metadata
    assert "variables_file_hash" in record.metadata
    original_hash = record.metadata["variables_file_hash"]
    assert original_hash == get_normalized_file_hash(variables_file)
    
    # Modify the variables file
    new_variables_content = '{ proxy_url: "http://newproxy.example.com:9090" }'
    variables_file.write_text(new_variables_content)
    new_hash = get_normalized_file_hash(variables_file)
    assert new_hash != original_hash, "Variables file hash should change after modification"
    
    # Update the variables in the renderer
    new_variables = {"proxy_url": "http://newproxy.example.com:9090"}
    renderer_2 = TemplateRenderer(
        variables=new_variables,
        variables_file_path=variables_file
    )
    
    # Touch one of the rendered files to mark it unchanged (simulating no source change)
    if render_tasks:
        # Mark destination files to appear unchanged to test that variables change triggers render
        for task in render_tasks:
            task.dst.write_text(RENDERED_CONTENT)
    
    # Second render with changed variables file
    record_2 = renderer_2.render(tasks=render_tasks, last_record=record)
    
    # Verify new variables file hash is stored
    assert "variables_file_hash" in record_2.metadata
    assert record_2.metadata["variables_file_hash"] == new_hash
    assert record_2.metadata["variables_file_hash"] != original_hash
    
    # Verify that files were re-rendered with new content
    expected_new_content = "Proxy URL: http://newproxy.example.com:9090"
    for task in render_tasks:
        content = task.dst.read_text()
        assert content == expected_new_content, (
            f"Expected {task.dst} to contain '{expected_new_content}', but got '{content}'"
        )


def test_render_without_variables_file(system: str, filesystem: FakeFilesystem) -> None:
    """Test that rendering works correctly when no variables file is provided."""
    from recnys.io.record import ExecutionRecord
    from recnys.render.renderer import TemplateRenderer
    from recnys.testing.build.arrange import make_render_tasks
    from recnys.testing.load.constants import LOADED_VARIABLES
    from recnys.testing.render.arrange import create_source_files
    
    # Setup
    render_tasks = make_render_tasks(system=system)
    create_source_files(filesystem=filesystem, tasks=render_tasks)
    
    # Render without variables file path
    renderer = TemplateRenderer(variables=LOADED_VARIABLES, variables_file_path=None)
    record = ExecutionRecord()
    record = renderer.render(tasks=render_tasks, last_record=record)
    
    # Verify files were rendered
    assert_rendered_correctly(tasks=render_tasks)
    
    # Verify no variables file hash in metadata
    assert "variables_file_hash" not in record.metadata
