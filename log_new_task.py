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


class LogTask:
    def __init__(self, user_input: UserInput):
        self.user_input = user_input

        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        prompts = PromptLibrary()

        task_extraction_system = SystemMessagePromptTemplate.from_template(
            prompts.task_extraction_system()
        )
        task_extraction_human = HumanMessagePromptTemplate.from_template(
            prompts.task_extraction_human()
        )
        task_crm_formatter_system = SystemMessagePromptTemplate.from_template(
            prompts.task_crm_formatter_system()
        )
        task_crm_formatter_human = HumanMessagePromptTemplate.from_template(
            prompts.task_crm_formatter_human()
        )
        task_judge_system = SystemMessagePromptTemplate.from_template(
            prompts.task_judge_system()
        )
        task_judge_human = HumanMessagePromptTemplate.from_template(
            prompts.task_judge_human()
        )
        task_finalizer_system = SystemMessagePromptTemplate.from_template(
            prompts.task_finalizer_system()
        )
        task_finalizer_human = HumanMessagePromptTemplate.from_template(
            prompts.task_finalizer_human()
        )

        self.task_extraction_prompt = ChatPromptTemplate.from_messages(
            [task_extraction_system, task_extraction_human]
        )
        self.task_crm_formatter_prompt = ChatPromptTemplate.from_messages(
            [task_crm_formatter_system, task_crm_formatter_human]
        )
        self.task_judge_prompt = ChatPromptTemplate.from_messages(
            [task_judge_system, task_judge_human]
        )
        self.task_finalizer_prompt = ChatPromptTemplate.from_messages(
            [task_finalizer_system, task_finalizer_human]
        )

        processor = PreProcessor(user_input)
        self.pre_processed = processor.pre_processing_output()

        self.task_extraction_chain = (
                self.task_extraction_prompt
                | self.model
                | JsonOutputParser()
        )
        self.task_crm_formatter_chain = (
                self.task_crm_formatter_prompt
                | self.model
                | JsonOutputParser()
        )
        self.task_judge_chain = (
                self.task_judge_prompt
                | self.model
                | JsonOutputParser()
        )
        self.task_finalizer_chain = (
                self.task_finalizer_prompt
                | self.model
                | JsonOutputParser()
        )


    def log_task_output(self):
        # best: compute once and reuse so you don't call LLM multiple times
        extractor = self.task_extraction_chain.invoke({
            "pre_processing_output": self.pre_processed
        })
        crm = self.task_crm_formatter_chain.invoke({
            "task_extraction_output": extractor
        })
        judge = self.task_judge_chain.invoke({
            "task_extraction_json": extractor,
            "crm_task_output_json": crm,
        })
        final = self.task_finalizer_chain.invoke({
            "task_extraction_json": extractor,
            "crm_task_output_json": crm,
            "judge_output_json": judge,
        })
        return final