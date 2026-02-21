from transformers import pipeline
import torch
import asyncio


_hf_pipeline = None
_local_lock = asyncio.Lock()

async def init_local_slm(
    model_name: str = "microsoft/phi-4-mini-instruct",
    device: str | int | torch.device = "cpu",
):
    global _hf_pipeline

    # Normalize device
    if isinstance(device, torch.device):
        device = -1 if device.type == "cpu" else 0
    elif isinstance(device, str):
        device = -1 if device == "cpu" else 0

    async with _local_lock:
        if _hf_pipeline is None:
            def _make_pipeline():
                return pipeline(
                    "text-generation",
                    model=model_name,
                    device=device
                )

            _hf_pipeline = await asyncio.to_thread(_make_pipeline)


async def call_local_slm(
    prompt: str,
    max_new_tokens: int = 128,
) -> dict:

    global _hf_pipeline

    if _hf_pipeline is None:
        raise RuntimeError("Model not initialized. Ensure init_local_slm() runs at startup.")

    def _generate():
        outputs = _hf_pipeline(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=_hf_pipeline.tokenizer.eos_token_id,
        )

        full_text = outputs[0]["generated_text"] if outputs else ""
        return full_text[len(prompt):]  # remove prompt echo

    generated = await asyncio.to_thread(_generate)
    return {"generated_text": generated.strip()}


async def construct_response(explanations : list[str], patient_case: dict[str, str]):
    prompt = "WARNING FLAGS:" 
    for explanation in explanations:
        prompt += explanation
        prompt += '\n\n'

    prompt += f"PATIENT OPERATION: {patient_case['operation']}\n\n"
    prompt += f"PATIENT NOTES: {patient_case['notes']}\n\n"

    prompt += "Act as a consulting nurse/physician. Construct a warning using the given context to warn and instruct the patient\'s caregiver."

    response = await call_local_slm(prompt)

    return response