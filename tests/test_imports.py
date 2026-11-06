import ast,sys
from pathlib import Path
from fabric_inspection.vision.classical.engine import PROJECT_ROOT,ClassicalInspectionEngine

def test_source_has_no_research_or_deep_learning_imports():
    forbidden=('experiments','torch','torchvision','timm','singlenet','literature_candidates','periodic_candidate')
    for path in (PROJECT_ROOT/'src/fabric_inspection').rglob('*.py'):
        tree=ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                assert not any(s in ast.unparse(node).lower() for s in forbidden),(path,ast.unparse(node))

def test_frozen_model_loading_needs_only_final_modules():
    engine=ClassicalInspectionEngine()
    assert len(engine.models)==7
    assert not any(name=='torch' or name.startswith(('torch.','fabric_inspection.inference.','fabric_inspection.vision.singlenet.')) for name in sys.modules)
    assert not any('experiments' in str(getattr(module,'__file__','')) for module in sys.modules.values() if module is not None)
