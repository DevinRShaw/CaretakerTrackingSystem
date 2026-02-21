from transformers import pipeline
import torch
import asyncio


_hf_pipeline = None
_local_lock = asyncio.Lock()

async def call_local_slm(
    prompt: str,
    model_name: str = "gpt2",
    max_new_tokens: int = 128,
    device: str | int | torch.device = "cpu",
) -> dict:

    global _hf_pipeline

    # normalize device to pipeline's `device` arg (int: -1 for CPU)
    if isinstance(device, torch.device):
        device = -1 if device.type == "cpu" else 0
    elif isinstance(device, str):
        device = -1 if device == "cpu" else 0

    async with _local_lock:
        if _hf_pipeline is None:
            def _make_pipeline():
                return pipeline("text-generation", model=model_name, device=device)

            _hf_pipeline_local = await asyncio.to_thread(_make_pipeline)
            _hf_pipeline = _hf_pipeline_local

    def _generate():
        outputs = _hf_pipeline(prompt, max_new_tokens=max_new_tokens, do_sample=False)
        # pipeline returns list of dicts with 'generated_text'
        return outputs[0]["generated_text"] if outputs else ""

    generated = await asyncio.to_thread(_generate)
    return {"generated_text": generated}



async def construct_response(explanations : list[str], patient_case: dict[str, str]):
    prompt = 'WARNING FLAGS:' 
    for explanation in explanations:
        prompt += explanation
        prompt += '\n\n'

    prompt += f'PATIENT OPERATION: {patient_case['operation']}\n\n'
    prompt += f'PATIENT NOTES: {patient_case['notes']}\n\n'

    prompt += 'Act as a consulting nurse/physician. Construct a warning using the given context to warn and instruct the patient\'s caregiver.'

    return await call_local_slm(prompt)