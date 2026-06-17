import os
import sys
import numpy as np

# Windows DLL loading helper for Python 3.8+
if sys.platform == "win32":
    # Add common paths where we copied or located the VC++ Redistributable DLLs
    venv_dir = os.path.dirname(sys.executable)
    if os.path.exists(venv_dir):
        try:
            os.add_dll_directory(venv_dir)
        except Exception:
            pass
            
    ag_bin = os.path.expandvars(r"%APPDATA%\Antigravity\bin")
    if os.path.exists(ag_bin):
        try:
            os.add_dll_directory(ag_bin)
        except Exception:
            pass

    powertoys_path = os.path.expandvars(r"%LOCALAPPDATA%\PowerToys")
    if os.path.exists(powertoys_path):
        try:
            os.add_dll_directory(powertoys_path)
        except Exception:
            pass

class EmbeddingModel:
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = os.getenv("MINERVA_MODEL_DIR", os.path.expanduser("~/.minerva/models"))
        self.model_dir = model_dir
        self.model_path = os.path.join(self.model_dir, "onnx", "model.onnx")
        self.tokenizer_path = os.path.join(self.model_dir, "tokenizer.json")
        
        self._session = None
        self._tokenizer = None

    def ensure_model_downloaded(self):
        # We check both model.onnx and tokenizer.json
        if not os.path.exists(self.model_path) or not os.path.exists(self.tokenizer_path):
            from huggingface_hub import hf_hub_download
            print(f"Downloading BGE-small ONNX embedding model to {self.model_dir}...")
            os.makedirs(self.model_dir, exist_ok=True)
            
            # Download model.onnx
            hf_hub_download(
                repo_id="Xenova/bge-small-en-v1.5",
                filename="onnx/model.onnx",
                local_dir=self.model_dir,
            )
            
            # Download tokenizer.json
            hf_hub_download(
                repo_id="Xenova/bge-small-en-v1.5",
                filename="tokenizer.json",
                local_dir=self.model_dir,
            )
            print("Model files downloaded successfully!")

    @property
    def tokenizer(self):
        if self._tokenizer is None:
            self.ensure_model_downloaded()
            from tokenizers import Tokenizer
            self._tokenizer = Tokenizer.from_file(self.tokenizer_path)
        return self._tokenizer

    @property
    def session(self):
        if self._session is None:
            self.ensure_model_downloaded()
            import onnxruntime as ort
            opts = ort.SessionOptions()
            opts.log_severity_level = 3  # Suppress verbose warnings
            self._session = ort.InferenceSession(self.model_path, opts, providers=["CPUExecutionProvider"])
        return self._session

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a block of text (document/record). No prefix is prepended.
        """
        if not text or not text.strip():
            return np.zeros(384, dtype=np.float32)

        encoding = self.tokenizer.encode(text)
        input_ids = np.array([encoding.ids], dtype=np.int64)
        attention_mask = np.array([encoding.attention_mask], dtype=np.int64)
        token_type_ids = np.array([encoding.type_ids], dtype=np.int64)

        inputs = {}
        for model_input in self.session.get_inputs():
            name = model_input.name
            if name == "input_ids":
                inputs[name] = input_ids
            elif name == "attention_mask":
                inputs[name] = attention_mask
            elif name == "token_type_ids":
                inputs[name] = token_type_ids

        outputs = self.session.run(None, inputs)
        # BGE models use the CLS token (index 0) as the representation
        last_hidden_state = outputs[0]
        cls_vector = last_hidden_state[0, 0, :]
        
        # Unit normalization (L2)
        norm = np.linalg.norm(cls_vector)
        if norm > 0:
            cls_vector = cls_vector / norm
            
        return cls_vector.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embeds a search query with the required BGE retrieval prefix.
        """
        prefix = "Represent this sentence for searching relevant passages: "
        return self.embed_text(prefix + query)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Computes cosine similarity (dot product of pre-normalized vectors).
        """
        return float(np.dot(vec1, vec2))
