import os
from langchain_google_genai import GoogleGenerativeAI
# from langchain.chains import LLMChain
from langchain.schema.runnable import RunnableSequence
from langchain.prompts import PromptTemplate
from typing import List

# Set Gemini API Key (Make sure you set this before running)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAWvmUMGSTHPtRn0fQbKQtTyVHKPU-3ixU"

def generate_prompt(selected_options):
    prompt_base = """
    أنت خبير لغوي ومتخصص في التدقيق اللغوي للنصوص العربية. قم بتصحيح النص التالي وفقًا للقواعد التالية في إجابة واحدة فقط، وأعد الإجابة بصيغة JSON تحتوي على جزئين:
    إحترام الصيغة json إجباري.
  
    **ملاحظة:** يجب اتباع القواعد المحددة فقط بناءً على الخيارات التي اخترتها، ولا يتم إضافة قواعد أخرى غير المختارة.

    القواعد المتاحة:
    """
    
    # Define the rules
    rules = {
        1: "1. **القواعد النحوية**: التأكد من صحة التراكيب النحوية وفقًا لقواعد اللغة العربية الفصحى، مع الالتزام بما يلي:\n"
        "- ضبط العلاقات الإعرابية بين الكلمات وتحديد مواقع الرفع، النصب، والجر.\n"
        "- تصحيح أخطاء التعدي باللازم والمتعدي، والتأكد من استخدام حروف الجر الصحيحة.\n"
        "- تصحيح استخدام أدوات الشرط والتوكيد والنفي والجر بطريقة صحيحة.\n"
        "- التمييز بين الجمل الاسمية والفعلية وضبط مكوناتها النحوية.\n"
        "\n**أمثلة على التصحيحات المطلوبة:**\n"
        " ❌ 'كان الطلابْ نشيطون' → ✅ 'كانَ الطلّابُ نَشِيطِينَ' (تصحيح الإعراب)\n"
        " ❌ 'أريد أن تذهبَ إلى السوقِ' → ✅ 'أريدُ أن تذهبَ إلى السوقِ' (تصحيح التعدي بالفعل)\n",

        2: "2. **الإملاء**: اكتشاف وتصحيح الأخطاء الإملائية لضمان كتابة الكلمات بشكل صحيح، مع الالتزام بما يلي:\n"
        "- التمييز بين التاء المربوطة والهاء والتاء المفتوحة.\n"
        "- تصحيح الأخطاء في كتابة همزات القطع والوصل وفقًا للقواعد.\n"
        "- التحقق من كتابة الألف المقصورة والياء بشكل صحيح.\n"
        "- تصحيح الأخطاء الشائعة في كتابة الأعداد بالحروف.\n"
        "\n**أمثلة على التصحيحات المطلوبة:**\n"
        " ❌ 'ذهب الئ المدرسه' → ✅ 'ذهب إلى المدرسة'\n"
        " ❌ 'هذا هو ابني ياسر' → ✅ 'هذا هو ابني ياسرٌ' (إضافة التنوين الصحيح)\n",

        3: "3. **التشكيل**: إضافة التشكيل الصحيح بشكل كامل وفقًا للقواعد الصرفية والنحوية، مع الالتزام بما يلي:\n"
        "- وضع الحركات المناسبة لكل حرف وفقًا للسياق النحوي والصرفي.\n"
        "- عدم إضافة سكون زائد في نهاية الكلمات إلا إذا كان مطلوبًا وفقًا للقواعد.\n"
        "- التأكد من وضع الشدة (ّ) في مواضعها الصحيحة عند الحاجة.\n"
        "- تصحيح التنوين (ً، ٍ، ٌ) بحيث يكون متوافقًا مع السياق.\n"
        "- التفريق بين الكلمات المتشابهة بناءً على التشكيل الصحيح (مثل: عَلِمَ - عَلَمٌ - عِلْمٌ).\n"
        "\n**أمثلة على التصحيحات المطلوبة:**\n"
        " ❌ 'المعلِمْ' → ✅ 'المُعَلِّمُ' (تصحيح الشدة وتغيير الحركات)\n"
        " ❌ 'العلمُ هو نورْ' → ✅ 'العِلْمُ هو نُورٌ' (إصلاح الحركات وإضافة التنوين)\n",

        4: "4. **علامات الترقيم**: تصحيح وتحسين استخدام علامات الترقيم لضمان وضوح المعنى، مع الالتزام بما يلي:\n"
        "- إضافة الفاصلة (،) عند الحاجة لفصل الجمل التوضيحية.\n"
        "- وضع النقطة (.) في نهاية الجملة المنتهية.\n"
        "- تصحيح علامات التعجب (!) والاستفهام (؟) وفقًا للسياق.\n"
        "- التأكد من عدم وضع أكثر من علامة ترقيم متتالية بشكل غير صحيح.\n"
        "\n**أمثلة على التصحيحات المطلوبة:**\n"
        " ❌ 'متى ستذهب الى المنزل,' → ✅ 'متى ستذهب إلى المنزل؟'\n"
        " ❌ 'ما أجمل هذا المكان؟؟' → ✅ 'ما أجمل هذا المكان!'\n",

        5: "5. **تحسين الأسلوب**: جعل النص أكثر سلاسة ووضوحًا من خلال:\n"
        "- إعادة صياغة الجمل الطويلة لتكون أكثر وضوحًا.\n"
        "- استخدام مفردات أكثر دقة وإيجازًا دون الإخلال بالمعنى.\n"
        "- تحسين التناسق بين الجمل والفقرات لخلق ترابط سلس.\n"
        "\n**أمثلة على التحسينات المطلوبة:**\n"
        " ❌ 'هذا الشيء الذي رأيته اليوم كان رائعاً جداً حقاً' → ✅ 'كان المشهد الذي رأيته اليوم رائعًا للغاية.'\n",

        6: "6. **توحيد المصطلحات**: التأكد من استخدام المصطلحات بشكل متناسق داخل النص، مع الالتزام بما يلي:\n"
        "- التأكد من استخدام نفس المصطلح عند الإشارة إلى نفس المفهوم.\n"
        "- توحيد أسماء الأماكن والأعلام حتى لا يحدث تناقض داخل النص.\n"
        "- توحيد كتابة الكلمات التي قد تُكتب بأكثر من شكل دون اختلاف في المعنى.\n"
        "\n**أمثلة على التصحيحات المطلوبة:**\n"
        " ❌ 'الذكاء الاصطناعي - الذكاء الصناعي' → ✅ 'الذكاء الاصطناعي' (توحيد المصطلحات)\n",

        7: "7. **إزالة التكرار**: تجنب تكرار الكلمات أو العبارات غير الضرورية، مع الالتزام بما يلي:\n"
        "- حذف التكرار غير الضروري الذي لا يضيف معنى جديدًا.\n"
        "- إعادة صياغة الجمل بحيث تكون أكثر إيجازًا ووضوحًا.\n"
        "\n**أمثلة على التصحيحات المطلوبة:**\n"
        " ❌ 'ذهب إلى السوق ثم ذهب إلى المنزل ثم ذهب إلى المدرسة' → ✅ 'ذهب إلى السوق، ثم المنزل، ثم المدرسة.'\n"
        " ❌ 'أحب القراءة، لأن القراءة مفيدة، والقراءة تجعلني مثقفًا' → ✅ 'أحب القراءة لأنها مفيدة وتزيد ثقافتي.'\n",

        8: "8. **تصحيح الترجمة (إن وجدت)**: التأكد من أن الترجمة صحيحة ومتماشية مع السياق، مع الالتزام بما يلي:\n"
        "- تصحيح الأخطاء الناتجة عن الترجمة الحرفية غير الدقيقة.\n"
        "- إعادة صياغة العبارات بحيث تتناسب مع الأسلوب العربي الفصيح.\n"
        "- التأكد من نقل المعنى بشكل دقيق دون تحريف أو فقدان التفاصيل المهمة.\n"
        "\n**أمثلة على التصحيحات المطلوبة:**\n"
        " ❌ 'I see the world with new eyes' → ❌ 'أنا أرى العالم بعيون جديدة' → ✅ 'أنظر إلى العالم برؤية جديدة.'\n"
    }


    # Initialize the prompt text
    prompt_text = prompt_base
    
    # If 0 is in the selected options, include all rules
    if 0 in selected_options:
        selected_options = rules.keys()  # Set the selected options to all rules
    
    # Add the selected rules
    for option in selected_options:
        if option in rules:
            prompt_text += rules[option]
    
    # Add the input text and the required JSON output format
    prompt_text += "\n**النص المدخل:** {text}\n\n**الإخراج المطلوب (بصيغة JSON):**\n{{\n    \"corrected_text\": \"النص المصحح هنا\",\n    \"details\": [\"شرح التعديلات التي تم إجراؤها على النص.\"]\n}}"
    prompt_text += "احترام الصيغة json إجباري."
    
    
    return prompt_text


def generate_query(selected_options: List[int], text: str) -> str:
    prompt_text = generate_prompt(selected_options)

    # Initialize Gemini
    llm = GoogleGenerativeAI(model="gemini-2.0-flash")

    # Define Prompt Template
    prompt = PromptTemplate.from_template(prompt_text)

    # Create Chain
    # chain = LLMChain(llm=llm, prompt=prompt)
    chain = RunnableSequence(prompt | llm)

    # Run Query
    # response = chain.run(text)
    response = chain.invoke(text)
    return response

# if __name__ == "__main__":
#     user_input = input("أدخل نص للتصحيح: ")
#     corrected_text = correct_text_with_gemini([0],user_input)
#     print("\nالنص الخاطئ:")
#     print(user_input)
#     print("\nالنص المصحح:")
#     print(corrected_text)