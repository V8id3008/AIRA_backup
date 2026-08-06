class ResponseBuilder:
    """
    Builds the final prompt sent to the LLM.
    """

    def build(
        self,
        user_input: str,
        context: str = "",
        research: str = ""
    ) -> str:

        sections = []

        if context:
            sections.append(context)

        if research:
            sections.append(
                "===== RESEARCH =====\n"
                + research
            )

        sections.append(
            "===== USER REQUEST =====\n"
            + user_input
        )

        return "\n\n".join(sections)