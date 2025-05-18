import tiktoken
import subprocess

class LocalSummarize:
    def __init__(self, model_name="llama2"):
        self.model_name = model_name
        self.encoding = tiktoken.get_encoding("cl100k_base")  
    def count_tokens(self, text):
        return len(self.encoding.encode(text))

    def chunk_text(self, text, max_tokens=500):
        tokens = self.encoding.encode(text)
        chunks = []

        current_chunk = []
        current_token_count = 0

        for token in tokens:
            if current_token_count + 1 <= max_tokens:
                current_chunk.append(token)
                current_token_count += 1
            else:
                chunks.append(self.encoding.decode(current_chunk))
                current_chunk = [token]
                current_token_count = 1

        if current_chunk:
            chunks.append(self.encoding.decode(current_chunk))

        return chunks

    def call_ollama(self, prompt):
        """
        Calls Ollama local model via subprocess with a prompt.
        """
        command = [
            "ollama",
            "run",
            self.model_name,
        ]
        try:
            result = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=180  # prevent hanging
            )
            if result.returncode != 0:
                raise RuntimeError(f"Ollama call failed: {result.stderr}")
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "Error: Model timed out while generating response."
        except Exception as e:
            return f"Error: {str(e)}"

    def summarize_text(self, text, max_chunk_size=500, max_combined_summary_size=4000):
        prompt_template = "Summarize briefly:\n\n{}"

        def recursive_summarize(text):
            chunks = self.chunk_text(text, max_chunk_size)
            summaries = []

            for chunk in chunks:
                prompt = prompt_template.format(chunk)
                summary = self.call_ollama(prompt)
                summaries.append(summary)

            combined_summary = " ".join(summaries)

            if self.count_tokens(combined_summary) > max_combined_summary_size:
                return recursive_summarize(combined_summary)
            else:
                return combined_summary
        # First round of summarization
        final_summary = recursive_summarize(text)

        # Refine it further for coherence
        cohesion_prompt = f"{final_summary}\n\nMake this more concise and clear in 2 paragraphs:"
        rewritten_summary = self.call_ollama(cohesion_prompt)

        return rewritten_summary

