baseGrammar = r"""
          QueryType: {<W..*>+<JJ.?>?}               # Chunk "wh-words" including modifiers like "How many"
          NP: {<DT>?<PR.*>?<JJ.?>*<N.*>+}           # Chunk sequences of DT or JJ followed by one or more nouns
          PP: {<IN><NP>}                            # Chunk prepositions followed by NP
          VP: {<V.*><NP|PP|CLAUSE>+}                # Chunk verbs and their arguments
          CLAUSE: {<NP><VP>}                        # Chunk NP, VP
          """
print(baseGrammar)