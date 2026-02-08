# Architectural Solution: Multi-Agent LLM System for Excel to StepWise JSON Conversion
Author: Manus AI  
Date: February 7, 2026

## 1. Introduction: The Core Challenge
Your current prototype for converting Excel-based actuarial models into StepWise JSON payloads faces a significant limitation: any minor change in the Excel model necessitates a complete rebuild of the entire JSON payload. This process is inefficient, error-prone, and difficult to scale, especially as the complexity of the actuarial models grows. A change to a single formula should not require regenerating the entire structure.

Your technical manager has proposed a more sophisticated and robust solution that leverages a multi-agent Large Language Model (LLM) architecture. This approach is designed to be modular, scalable, and significantly more efficient at handling incremental changes. This document provides a comprehensive breakdown of that proposed architecture, explaining how the components work together to solve your core problem.

## 2. The Multi-Agent "Divide and Conquer" Strategy
The fundamental principle behind your manager's suggestion is "divide and conquer." Instead of having one monolithic process (or a single, giant LLM prompt) try to understand and convert the entire complex Excel file at once, you break the problem down into smaller, manageable sub-tasks. Each sub-task is then assigned to a specialized "agent."

An agent, in this context, is a dedicated LLM instance given a very specific role and a highly-focused prompt. For example:
- One agent is an expert at identifying and structuring lookup tables.
- Another agent is an expert at parsing and translating Excel formulas.
- A third agent specializes in handling factors and variables.

These specialized agents work in parallel, each producing a small, self-contained fragment of the final JSON. An orchestrator then assembles these fragments into the complete, valid StepWise payload. This modularity is the key to solving your problem.

## 3. Architectural Diagram
The following diagram illustrates the end-to-end workflow of the proposed multi-agent system.

## 4. Detailed Step-by-Step Breakdown
Let's walk through each phase of the architecture shown in the diagram.

### Step 1: Pre-processing
This initial step is about preparing the raw data for the LLM agents. An LLM works best with clean, structured text, not proprietary binary formats like .xlsx.

1. **Excel Parser:** A script (e.g., using a Python library like openpyxl or pandas) reads the Excel file. It doesn't try to understand the logic; it simply extracts the contents of each sheet.
2. **Structured Data Output:** The parser separates different types of data into distinct, simple formats, primarily CSVs. For instance:
   - `lookups.csv`: Contains all the data from named ranges or identified lookup tables.
   - `factors.csv`: A simple key-value list of all input factors or variables.
   - `formulas.csv`: A list of cells containing formulas, along with the formulas themselves (e.g., Cell: "C5", Formula: "=VLOOKUP(A5, Sheet2!$A$1:$B$10, 2, FALSE) * Factors!$B$1").

### Step 2: Orchestration and Task Decomposition
This is the brain of the operation. The Orchestrator Agent is a higher-level agent that manages the overall workflow.

1. The Orchestrator receives the structured data (the set of CSVs) from the pre-processing step.
2. It analyzes the files and understands the scope of the conversion task.
3. It then decomposes the main goal ("Convert this model") into specific sub-tasks and delegates them to the appropriate specialized agents. For example, it sends `factors.csv` to the Factor Agent, `lookups.csv` to the Lookup Table Agent, and so on.

### Step 3: Specialized JSON Generation (in Parallel)
This is where the "magic" happens. Each specialized agent works independently and simultaneously on its assigned task.

- **Factor Agent:** Receives `factors.csv`. Its sole job is to use its highly-tuned prompt to convert this simple key-value data into the specific JSON structure that StepWise expects for defining factors. It outputs a `factor_fragment.json`.
- **Lookup Table Agent:** Receives `lookups.csv`. It is an expert at creating the StepWise JSON for table lookups. It outputs a `lookup_fragment.json`.
- **Formula/Calculation Agent:** This is the most complex agent. It receives the `formulas.csv` data. Its prompt is engineered to be an expert in translating Excel formula syntax (like VLOOKUP, IF, SUMIFS) into the equivalent StepWise calculation language within a JSON structure. It outputs a `calculation_fragment.json`.

### Step 4: Assembly and Validation
Once the specialized agents have completed their work, their outputs need to be combined.

1. **JSON Assembler:** This is a relatively simple component. It takes the various JSON fragments (`factor_fragment.json`, `lookup_fragment.json`, etc.) and intelligently merges them into a single, complete JSON document based on the required StepWise payload structure.
2. **JSON Validator:** Before sending the payload to StepWise, it's crucial to validate it. This component checks the assembled JSON against a known StepWise JSON Schema (if one exists) or runs a series of checks to ensure all required fields are present and correctly formatted. This prevents sending invalid data to the API.

### Step 5: Final Output
The final, validated JSON payload is now ready and is sent to the StepWise API endpoint for import.

## 5. How This Solves Your Core Problem: Handling Small Changes
Now, let's address your primary limitation. What happens when an actuary changes just one formula in the Excel sheet?

In the multi-agent architecture, the process is incredibly efficient:

1. You run a file-watcher or a git-diff process that detects a change was made only to a specific cell (e.g., C5) in the Excel file.
2. The pre-processing step runs, but it sees that `lookups.csv` and `factors.csv` are unchanged. It only produces a new, very small `formulas.csv` that perhaps contains only the single changed formula.
3. The Orchestrator Agent is smart. It sees that only the formula data has changed.
4. It only activates the Formula/Calculation Agent. The Factor and Lookup Table agents are not invoked, saving time and processing cost.
5. The Formula Agent generates a tiny `calculation_fragment.json` for the single updated formula.
6. The JSON Assembler now has a more interesting task. It takes the existing, full JSON payload from the last successful run and intelligently patches it, replacing only the specific calculation block that has changed with the new fragment.
7. The updated payload is validated and sent to the StepWise API.

This "patching" approach, enabled by the modularity of the agents, means you never have to rebuild the entire JSON from scratch for a small change. You only regenerate the fragment that corresponds to the change.

## 6. The Importance of a "Solid Prompt"
Your manager's emphasis on a "solid prompt" is critical. The reliability of this entire system depends on how well you instruct each specialized agent. Here are examples of what those prompts might look like.

### Example Prompt for the Lookup Table Agent
You are an expert StepWise JSON developer. Your sole responsibility is to convert CSV data representing a lookup table into the valid StepWise JSON format for a "Table Lookup" component. You will be given the table name and the table data in CSV format. Do not add any other components. Do not explain your work. Only output the raw JSON object.

**Table Name:** `AgeBanding`

**CSV Data:**
```
MinAge,MaxAge,Factor
0,17,1.2
18,24,1.1
25,35,1.0
36,45,1.15
```

**Your JSON Output:**

### Example Prompt for the Formula/Calculation Agent
You are an expert StepWise JSON developer specializing in calculation logic. Your task is to convert a single Excel formula into the corresponding StepWise JSON calculation block. You must accurately translate Excel functions like VLOOKUP, IF, and standard arithmetic operators into their StepWise equivalents.

**Excel Formula:** `=IF(VLOOKUP(A5, AgeBanding, 2, FALSE) > 1.1, "High Risk", "Standard Risk")`

**Context:**
- `A5` refers to the "ApplicantAge" input variable.
- `AgeBanding` is a pre-defined StepWise Table Lookup component.

**Your JSON Output:**

## 7. Conclusion
By shifting from a monolithic conversion process to a modular, multi-agent architecture, you directly address the inefficiency and fragility of your current system. This "divide and conquer" strategy, powered by specialized LLM agents, allows you to isolate changes, regenerate only the necessary JSON fragments, and intelligently patch the final payload.
