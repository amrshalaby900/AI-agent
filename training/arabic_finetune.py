from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. إعدادات النموذج (اختيار أقوى النماذج للغة العربية)
model_name = "unsloth/DeepSeek-R1-Distill-Qwen-7B-bnb-4bit"
max_seq_length = 2048
dtype = None # None للتعرف التلقائي
load_in_4bit = True # استخدام 4-bit لتقليل استهلاك الذاكرة

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 2. إضافة تقنية LoRA للتطوير السريع
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # رتبة التكيف (Rank)
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)

# 3. تجهيز البيانات العربية (مثال: بيانات محادثات عربية)
# يمكنك استبدال هذا ببياناتك الخاصة
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        # تنسيق مخصص للغة العربية
        text = f"### تعليمات:\n{instruction}\n\n### مدخلات:\n{input}\n\n### استجابة:\n{output}"
        texts.append(text)
    return { "text" : texts, }

# تحميل قاعدة بيانات عربية (مثال)
dataset = load_dataset("yahma/alpaca-arabic", split = "train")
dataset = dataset.map(formatting_prompts_func, batched = True,)

# 4. إعدادات التدريب
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # عدد الخطوات (للتجربة)
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

# 5. بدء التدريب (صناعة النموذج العربي الأقوى)
print("جاري بدء عملية التدريب لتطوير النموذج العربي...")
trainer_stats = trainer.train()

# 6. حفظ النموذج النهائي
model.save_pretrained("arabic_model_final")
tokenizer.save_pretrained("arabic_model_final")
print("تم حفظ النموذج العربي المطور بنجاح في مجلد: arabic_model_final")
