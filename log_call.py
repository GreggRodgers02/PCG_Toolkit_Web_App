from prompt_library import PromptLibrary
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pre_processing import PreProcessor

load_dotenv()

class UserInput(BaseModel):
    user_input: str


class LogCall:
    def __init__(self, user_input: UserInput):
        self.user_input = user_input

        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        prompts = PromptLibrary()

        call_crm_formatter_system = SystemMessagePromptTemplate.from_template(
            prompts.call_crm_formatter_system()
        )
        call_crm_formatter_human = HumanMessagePromptTemplate.from_template(
            prompts.call_crm_formatter_human()
        )
        call_judge_system = SystemMessagePromptTemplate.from_template(
            prompts.call_judge_system()
        )
        call_judge_human = HumanMessagePromptTemplate.from_template(
            prompts.call_judge_human()
        )
        call_finalizer_system = SystemMessagePromptTemplate.from_template(
            prompts.call_finalizer_system()
        )
        call_finalizer_human = HumanMessagePromptTemplate.from_template(
            prompts.call_finalizer_human()
        )

        self.call_crm_formatter_prompt = ChatPromptTemplate.from_messages(
            [call_crm_formatter_system, call_crm_formatter_human]
        )
        self.call_judge_prompt = ChatPromptTemplate.from_messages(
            [call_judge_system, call_judge_human]
        )
        self.call_finalizer_prompt = ChatPromptTemplate.from_messages(
            [call_finalizer_system, call_finalizer_human]
        )

        processor = PreProcessor(user_input)
        self.pre_processed = processor.pre_processing_output()

        self.call_crm_formatter_chain = (
                self.call_crm_formatter_prompt
                | self.model
                | JsonOutputParser()
        )

        self.call_judge_chain = (
                self.call_judge_prompt
                | self.model
                | JsonOutputParser()
        )
        self.call_finalizer_chain = (
                self.call_finalizer_prompt
                | self.model
                | JsonOutputParser()
        )


    def log_call_output(self):
        try:
            # best: compute once and reuse so you don't call LLM multiple times
            crm = self.call_crm_formatter_chain.invoke({
                "pre_processing_output": self.pre_processed
            })
            judge = self.call_judge_chain.invoke({
                "pre_processing_output": self.pre_processed,
                "call_crm_formatter_output": crm,
                "user_input": self.user_input.user_input,
            })
            final = self.call_finalizer_chain.invoke({
                "processed_call_json": self.pre_processed,
                "crm_output_json": crm,
                "judge_output_json": judge,
                "user_input": self.user_input.user_input,
            })
            return final
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "subject": "Error processing call",
                "call_type": "Other",
                "comments": f"An error occurred while analyzing the call: {str(e)}. Please try again or use a shorter transcript.",
                "name": "",
                "company": ""
            }