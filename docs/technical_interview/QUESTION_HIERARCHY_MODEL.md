# Question Hierarchy Model (Day 46)

Domain
  Topic
    Question type (experience, conceptual, scenario)
      Level (L1, L2, L3)
        Question (text, key points, follow-up)

Example path: MERN > React > conceptual > L2 > "How does useEffect work?"

## Question record
| Field | Meaning |
|---|---|
| id | unique, e.g. mern_react_con_l2_01 |
| type | experience, conceptual or scenario |
| level | L1, L2 or L3 |
| text | the question |
| key_points | ideas a good answer covers |
| follow_up | first follow-up question |

## Selection rules
1. Pick domain from the job.
2. Pick type from the current phase.
3. Pick level from experience band and last answer score.
4. Never repeat a question in one interview.
5. If no question fits, use the nearest level.

Sample data: data/technical_interview/question_hierarchy.json