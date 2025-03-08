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
        1: "1. **القواعد النحوية**: تأكد من صحة التراكيب النحوية.\n",
        2: "2. **الإملاء**: اكتشاف وتصحيح الأخطاء الإملائية.\n",
        3: "3. **التشكيل**: ضبط الحركات عند الحاجة لضمان وضوح المعنى.\n",
        4: "4. **علامات الترقيم**: تصحيح وتحسين استخدام الفواصل، النقاط، وعلامات الاستفهام.\n",
        5: "5. **تحسين الأسلوب**: جعل النص أكثر سلاسة وفهمًا.\n",
        6: "6. **توحيد المصطلحات**: التأكد من أن المصطلحات تُستخدم بشكل متناسق.\n",
        7: "7. **إزالة التكرار**: تجنب تكرار الكلمات أو الجمل دون داعٍ.\n",
        8: "8. **تصحيح الترجمة (إن وجدت)**: التأكد من أن المعنى دقيق ويتماشى مع السياق.\n"
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