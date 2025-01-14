from PyPDF2 import PdfReader
import json
import re

reader = PdfReader("MCM_TS_MCOFF.pdf")
page = reader.pages[0]
text = page.extract_text()

text = re.sub(r"\s+", " ", text)

print(text)


def parse_transcript(text):
    result = {
        "issued_to": "",
        "student_info": {},
        "transcript": []
    }
    
    # Extract "Issued To"
    issued_to_match = re.search(r"Issued To:\s*(.+?)\s+Name:", text)
    if issued_to_match:
        result["issued_to"] = issued_to_match.group(1).strip()

    # Extract student info
    student_info_match = re.search(
        r"Name:\s*Student ID No:\s*OEN:\s*Birth Day:\s*Print Date:\s*([\w\s]+?)\s+(\d+)\s*(?:([\d\w]*)\s+)?(\d+\s+\w+)\s+(\d+\s+\w+\s+\d+)",
        text
    )
    if student_info_match:
        result["student_info"] = {
            "name": student_info_match.group(1).strip(),
            "student_id": student_info_match.group(2).strip(),
            "oen": student_info_match.group(3).strip() if student_info_match.group(3) else None,
            "birth_date": student_info_match.group(4).strip(),
            "print_date": student_info_match.group(5).strip()
        }

    # Split transcript into terms
    terms = re.split(r"---\s*(\d{4} (Fall|Winter))\s*---", text)
    for i in range(1, len(terms), 3):
        term_year = terms[i].strip()
        term_details = terms[i + 2].strip()
        
        program_match = re.search(r"Program:\s*(.+?) Plan:", term_details)
        plan_match = re.search(r"Plan:\s*(.+?) Course", term_details)

        term_data = {
            "term": term_year,
            "program": program_match.group(1).strip() if program_match else None,
            "plan": plan_match.group(1).strip() if plan_match else None,
            "courses": [],
            "totals": {}
        }

        # Extract courses
        course_matches = re.findall(
            r"([A-Z]+[A-Z0-9]+\s\d+[A-Z0-9]+)\s+(.+?)\s+(\d+\.\d+/\d+\.\d+)\s+([A-Z+]+|COM)",
            term_details
        )
        for course in course_matches:
            course_code, title, units, grade = course
            term_data["courses"].append({
                "course_code": course_code.strip(),
                "title": title.strip(),
                "units": units.strip(),
                "grade": grade.strip()
            })

        # Extract term totals
        totals_match = re.search(
            r"Term Totals\s+(\d+\.\d+/\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)",
            term_details
        )
        if totals_match:
            term_data["totals"] = {
                "attm_earned_units": totals_match.group(1),
                "gpa_units": totals_match.group(2),
                "total_points": totals_match.group(3),
                "gpa": totals_match.group(4)
            }

        result["transcript"].append(term_data)

    return result


transcript_json = parse_transcript(text)

# Output the JSON
print(json.dumps(transcript_json, indent=4))