from huggingface_hub import hf_hub_download

# Download model weights
path = hf_hub_download(
    repo_id="boomb0om/watermark-detection",
    filename="pytorch_model.bin"
)

print("Downloaded to:", path)