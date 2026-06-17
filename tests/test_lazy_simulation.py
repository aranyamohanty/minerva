import sys
import os
import tempfile
import shutil
from click.testing import CliRunner

def test_lazy_imports_and_cli():
    tmpdir = tempfile.mkdtemp()
    try:
        src_dir = os.path.abspath('minerva')
        dst_dir = os.path.join(tmpdir, 'minerva')
        shutil.copytree(src_dir, dst_dir)
        
        # Patch db.py to lazy-load numpy
        db_path = os.path.join(dst_dir, 'db.py')
        with open(db_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = "from __future__ import annotations\n" + content
        content = content.replace(
            'import numpy as np',
            'from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    import numpy as np'
        )
        content = content.replace(
            'def set_embedding(self, record_type: str, record_id: int, vector: np.ndarray):',
            'def set_embedding(self, record_type: str, record_id: int, vector: np.ndarray):\n        import numpy as np'
        )
        content = content.replace(
            "return np.frombuffer(row['vector_blob'], dtype=np.float32)",
            "import numpy as np\n        return np.frombuffer(row['vector_blob'], dtype=np.float32)"
        )
        content = content.replace(
            "return [(r['record_id'], np.frombuffer(r['vector_blob'], dtype=np.float32)) for r in rows]",
            "import numpy as np\n        return [(r['record_id'], np.frombuffer(r['vector_blob'], dtype=np.float32)) for r in rows]"
        )
        with open(db_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Patch embeddings.py to lazy-load onnxruntime, tokenizers, huggingface_hub
        emb_path = os.path.join(dst_dir, 'embeddings.py')
        with open(emb_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('import onnxruntime as ort', '#')
        content = content.replace('from tokenizers import Tokenizer', '#')
        content = content.replace('from huggingface_hub import hf_hub_download', '#')
        content = content.replace(
            'hf_hub_download(',
            'from huggingface_hub import hf_hub_download\n            hf_hub_download('
        )
        content = content.replace(
            'self._tokenizer = Tokenizer.from_file(self.tokenizer_path)',
            'from tokenizers import Tokenizer\n            self._tokenizer = Tokenizer.from_file(self.tokenizer_path)'
        )
        content = content.replace(
            'opts = ort.SessionOptions()',
            'import onnxruntime as ort\n            opts = ort.SessionOptions()'
        )
        with open(emb_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Patch prompt_builder.py to lazy-load tokenizers
        pb_path = os.path.join(dst_dir, 'prompt_builder.py')
        with open(pb_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace(
            'from tokenizers import Tokenizer',
            'from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from tokenizers import Tokenizer'
        )
        with open(pb_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Patch cli.py to lazy-load embeddings, retrieval, and prompt_builder
        cli_path = os.path.join(dst_dir, 'cli.py')
        with open(cli_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('from minerva.embeddings import EmbeddingModel', '#')
        content = content.replace('from minerva.retrieval import RetrievalEngine', '#')
        content = content.replace('from minerva.prompt_builder import PromptBuilder', '#')
        content = content.replace(
            'embedder = EmbeddingModel()',
            'from minerva.embeddings import EmbeddingModel\n    embedder = EmbeddingModel()'
        )
        content = content.replace(
            'engine = RetrievalEngine(db, embedder)',
            'from minerva.embeddings import EmbeddingModel\n    from minerva.retrieval import RetrievalEngine\n    engine = RetrievalEngine(db, embedder)'
        )
        content = content.replace(
            'builder = PromptBuilder(db, engine, embedder.tokenizer)',
            'from minerva.embeddings import EmbeddingModel\n    from minerva.retrieval import RetrievalEngine\n    from minerva.prompt_builder import PromptBuilder\n    builder = PromptBuilder(db, engine, embedder.tokenizer)'
        )
        with open(cli_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Insert temp directory into sys.path to load our modified version
        sys.path.insert(0, tmpdir)
        
        # Save original sys.modules states
        orig_modules = {
            'onnxruntime': sys.modules.get('onnxruntime'),
            'tokenizers': sys.modules.get('tokenizers'),
            'huggingface_hub': sys.modules.get('huggingface_hub'),
            'numpy': sys.modules.get('numpy'),
        }
        
        # Block heavy modules to verify they are not imported
        sys.modules['onnxruntime'] = None
        sys.modules['tokenizers'] = None
        sys.modules['huggingface_hub'] = None
        sys.modules['numpy'] = None
        
        # Try importing and time it
        import time
        start_t = time.perf_counter()
        import minerva.cli as cli
        end_t = time.perf_counter()
        print(f"\n[SUCCESS] Imported contexts.cli successfully without importing heavy libraries!")
        print(f"Import time: {(end_t - start_t) * 1000:.2f} ms")
        
        # Verify sys.modules
        assert sys.modules['onnxruntime'] is None
        assert sys.modules['tokenizers'] is None
        assert sys.modules['huggingface_hub'] is None
        assert sys.modules['numpy'] is None
        
        # Run list goals
        runner = CliRunner()
        result = runner.invoke(cli.main, ['list', 'goals'])
        print(f"[SUCCESS] Command output:\n{result.output.strip()}")
        assert result.exit_code == 0

    finally:
        # Restore sys.modules
        for k in ['onnxruntime', 'tokenizers', 'huggingface_hub', 'numpy']:
            v = orig_modules.get(k)
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
        # Pop minerva submodules
        for k in list(sys.modules.keys()):
            if k.startswith('minerva'):
                sys.modules.pop(k, None)
        # Clean up path
        if tmpdir in sys.path:
            sys.path.remove(tmpdir)
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    test_lazy_imports_and_cli()
