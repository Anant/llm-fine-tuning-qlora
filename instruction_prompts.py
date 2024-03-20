outer_prompt = """This prompt should act as a classifier step in a larger goal to create an instruction set for fine-tuning an LLM. An instruction for fine-tuning is composed of 3 parts: the instruction itself is the thing a user would ask the LLM, the context, and the response from the LLM. The prompt should review the article included at the end of this prompt and classify which of the several instruction types can be extracted from the text. There should be enough information in the article to complete all three parts, instruction, context, and response of the instruction.

There are some instructions which can be gleaned from every article which will be reviewed:
1. Summarize a section of the article
2. Describe or summarize the impact of the article

Some instructions will only apply to certain articles depending on their contents:
3. Explain any Caveats or Cautions noted in the Article
4. Clarify Configuration Options
5. Explain the feature / Summarize the Feature
6. Explain a technical concept
7. Analyze and Summarize a Code Example
8. Compare and Contrast two entities in the article
9. Provide Practical Advice
10. Summarize the impact
11. Describe Integration impacts
12. Describe compatible technologies
13. Describe a practical use case for this tool
14. Help me implement a tool

The job of this specific prompt is to classify very explicitly which of the instruction prompts are the most appropriate for the specific article. They key to classification is to fit the specific content and structure of the article to the prompt. Assess the sections of the article, code examples, or features from the article. Tailored instructions that directly apply to the article's content should correlate to 1 or more of the prompts. Not every instruction type will apply to the specific article context.

The output of this prompt should be only the specific classifications indicating which of the prompts best apply to the specific article included below. It should be as simple as explicitly defining the type of instruction (including the number associated with the instruction) and doesn’t need to include a justification for the instruction.

Article:
"""
system_prompt = """
You are a technical writer designed to output JSON. Use the article below to generate a single JSON instruction based on article content to enhance an LLM's understanding and response capabilities regarding the NoSQL ecosystem, with a focus on Cassandra. The system should generate instructions in three parts that include the following parts:

Instruction (User Query): Clearly defined user queries should remain focused on eliciting expert-level insights into NoSQL concepts, practices, or comparisons without requiring lengthy explanations.
    
Context (Background Information and Article Excerpts): Expand this section to form the bulk of the instruction set. It should weave in detailed background information, incorporating specific excerpts from the article that cover key points, technical explanations, and real-world applications of Cassandra. This context must provide a comprehensive backdrop, setting the stage for a nuanced understanding of the query topic, highlighting Cassandra’s architecture, use cases, and its differentiation from traditional databases.

Response (LLM's Answer): Direct the LLM to generate responses that are concise, precise, and reflect a deep understanding of NoSQL technologies, particularly Cassandra. Responses should leverage the rich context provided, focusing on delivering actionable insights, clear comparisons, or succinct explanations. The response should avoid generalities and aim to provide specific, valuable knowledge that goes beyond the surface-level information, ideally in a few sentences.

Focus the instruction refinement on achieving a balance where the context-rich section educates and informs both the LLM and the users, while the response section showcases the LLM's ability to distill complex NoSQL concepts into accessible, expert advice or information. """
inner_prompt_pt1 = """Summarize a section of the article: Pick out the most important segment of the article and summarize the main idea of that segment."""
inner_prompt_pt2 = """Describe or summarize the impact of the article: Describe how this article's topic fits together with the larger tech ecosystem."""
inner_prompt_det_3 = """Explain any Caveats or Cautions noted in the Article: Describe a section of the article that warns the user of any unexpected pitfalls associated with tools or instructions in the article."""
inner_prompt_det_4 = """Clarify Configuration Options: Concentrate on explaining the variety of configuration settings available across NoSQL systems, highlighting how each setting impacts performance and utility."""
inner_prompt_det_5 = """Explain/Summarize a feature: Focus on elucidating specific features or aspects of NoSQL technologies, including Cassandra, providing a clear overview of their functions and benefits."""
inner_prompt_det_6 = """Explain a technical concept and aim to make complex technical concepts within the NoSQL realm, including those related to Cassandra, accessible and understandable to a broader audience."""
inner_prompt_det_7 = """Analyze and Summarize a Code Example: Pull a code snippet from the following article and annalyze what that code does."""
inner_prompt_det_8 = """Compare and Contrast two entities in the article: Compare their functionality, features, cost, or other relevant information about the entities - how are they different or similar."""
inner_prompt_det_9 = """Provide Practical Advice: Offer actionable, concrete advice and strategies for using NoSQL technologies effectively, drawing on industry best practices."""
inner_prompt_det_10 = """Summarize the impact: deliver a judgemental response that specifies what the impact/effect of what is discussed in the article."""
inner_prompt_det_11 = """Describe Integration Impacts: Discuss how integrating NoSQL technologies like Cassandra with other systems affects performance, capabilities, and architecture of systems that work with the NoSQL database."""
inner_prompt_det_12 = """Describe Compatible Technologies: Identify and elaborate on other technologies and tools that synergize well with NoSQL systems, focusing on interoperability and complementary use."""
inner_prompt_det_13 = """Describe a Practical Use Case for this Tool: Present real-world applications and scenarios demonstrating the effective use of NoSQL technologies in various contexts."""
inner_prompt_det_14 = """Help me Implement a Tool: Provide comprehensive, step-by-step guidance or troubleshooting assistance for implementing specific NoSQL solutions, including Cassandra, in diverse environments."""
inner_prompt_list = [inner_prompt_pt1, inner_prompt_pt2, inner_prompt_det_3, inner_prompt_det_4, inner_prompt_det_5, inner_prompt_det_6, inner_prompt_det_7, inner_prompt_det_8, inner_prompt_det_9, inner_prompt_det_10, inner_prompt_det_11, inner_prompt_det_12, inner_prompt_det_13, inner_prompt_det_14]
article_header = """
Article: 
"""
output_format_block = """
Return a JSON object with the following format:
{
"instruction": "<The Instruction (User Query)>",
"input": "<The Context (Background Information and Article Excerpts)>",
"output": "Response (LLM's Answer)"
}
"""

