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


class NextAction:
    def __init__(self, user_input: UserInput):
        self.user_input = user_input

        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        prompts = PromptLibrary()

        action_extraction_system = SystemMessagePromptTemplate.from_template(
            prompts.action_extractor_system()
        )
        action_extraction_human = HumanMessagePromptTemplate.from_template(
            prompts.action_extractor_human()
        )
        action_plan_building_system = SystemMessagePromptTemplate.from_template(
            prompts.action_plan_builder_system()
        )
        action_plan_building_human = HumanMessagePromptTemplate.from_template(
            prompts.action_plan_builder_human()
        )
        action_judge_system = SystemMessagePromptTemplate.from_template(
            prompts.action_judge_system()
        )
        action_judge_human = HumanMessagePromptTemplate.from_template(
            prompts.action_judge_human()
        )
        action_finalizer_system = SystemMessagePromptTemplate.from_template(
            prompts.action_finalizer_system()
        )
        action_finalizer_human = HumanMessagePromptTemplate.from_template(
            prompts.action_finalizer_human()
        )

        self.action_extraction_prompt = ChatPromptTemplate.from_messages(
            [action_extraction_system, action_extraction_human]
        )
        self.action_plan_building_prompt = ChatPromptTemplate.from_messages(
            [action_plan_building_system, action_plan_building_human]
        )
        self.action_judge_prompt = ChatPromptTemplate.from_messages(
            [action_judge_system, action_judge_human]
        )
        self.action_finalizer_prompt = ChatPromptTemplate.from_messages(
            [action_finalizer_system, action_finalizer_human]
        )

        processor = PreProcessor(user_input)
        self.pre_processed = processor.pre_processing_output()

        self.action_extraction_chain = (
                self.action_extraction_prompt
                | self.model
                | JsonOutputParser()
        )
        self.action_plan_building_chain = (
                self.action_plan_building_prompt
                | self.model
                | JsonOutputParser()
        )
        self.action_judge_chain = (
                self.action_judge_prompt
                | self.model
                | JsonOutputParser()
        )
        self.action_finalizer_chain = (
                self.action_finalizer_prompt
                | self.model
                | JsonOutputParser()
        )


    def next_action_output(self):
        # best: compute once and reuse so you don't call LLM multiple times
        extractor = self.action_extraction_chain.invoke({
            "pre_processing_output": self.pre_processed,
            "user_input": self.user_input.user_input
        })
        plan = self.action_plan_building_chain.invoke({
            "action_extractor_output": extractor
        })
        judge = self.action_judge_chain.invoke({
            "action_extractor_output": extractor,
            "action_plan_building_output": plan,
        })
        final = self.action_finalizer_chain.invoke({
            "action_extractor_output": extractor,
            "action_plan_building_output": plan,
            "action_judge_output": judge,
        })
        return final