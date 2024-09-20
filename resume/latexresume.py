from pylatex import Document, Section, Subsection, Itemize, Command
from pylatex.utils import NoEscape

def create_resume():
    doc = Document()

    # Adding Name and Contact Information
    doc.preamble.append(Command('title', 'Pavan Khairnar'))
    doc.preamble.append(Command('author', NoEscape(r'''
        Row House No. 3, Behind Dhanvantri Medical College, Kamatwade, Nashik \\
        Email: \href{mailto:pavansk00@gmail.com}{pavansk00@gmail.com} \\
        Phone: +91 8055719031 \\
        LinkedIn: \href{https://www.linkedin.com/in/pavan-khairnar-588077140/}{linkedin.com/in/pavan-khairnar-588077140}
    ''')))
    doc.preamble.append(Command('date', ''))

    doc.append(NoEscape(r'\maketitle'))

    # Professional Summary
    with doc.create(Section('Professional Summary', numbering=False)):
        doc.append((
            "I’m a game developer specializing in Python. I excel in creating game logic, mechanics, and APIs, working closely "
            "with game design teams to develop engaging features. My expertise includes both SQL and NoSQL databases for efficient "
            "data management, as well as building secure and scalable APIs. I also focus on real-time communication and microservices "
            "architecture, ensuring smooth and reliable operations."
        ))

    # Skills
    with doc.create(Section('Skills', numbering=False)):
        with doc.create(Itemize()) as itemize:
            skills = [
                "Python", "MySQL", "Linux", "System Design", "AWS",
                "Big Data", "Hadoop", "Spark", "Power BI", "Machine Learning"
            ]
            for skill in skills:
                itemize.add_item(skill)

    # Experience
    with doc.create(Section('Experience', numbering=False)):
        with doc.create(Subsection('Software Engineer', numbering=False)):
            doc.append('IVY Comptech Private Limited, Hyderabad | Dec 2021 - Present')
            with doc.create(Itemize()) as itemize:
                responsibilities = [
                    "Design, develop, and maintain game logic and mechanics using Python.",
                    "Collaborate with game design teams to implement game features and functionalities.",
                    "Develop and maintain APIs to support web and game functionalities.",
                    "Manage databases (SQL & NoSQL) for efficient data storage and retrieval.",
                    "Ensure the security, reliability, and scalability of APIs.",
                    "Collaborate with front-end developers for seamless web application integration.",
                    "Monitor and analyze logs and database data to resolve production issues.",
                    "Implement logging and monitoring solutions to ensure system reliability.",
                    "Develop and implement WebSocket-based solutions for real-time communication.",
                    "Design and implement microservices architecture for scalable applications."
                ]
                for responsibility in responsibilities:
                    itemize.add_item(responsibility)

        with doc.create(Subsection('POP Engineer', numbering=False)):
            doc.append('Tikona Infinet Private Limited, Nashik | Sept 2018 - July 2021')
            with doc.create(Itemize()) as itemize:
                responsibilities = [
                    "Network monitoring, router configuration, RF device LTE link setup.",
                    "Network maintenance, troubleshooting, Linux machine configuration, and firewall services.",
                    "Provided technical support."
                ]
                for responsibility in responsibilities:
                    itemize.add_item(responsibility)

    # Education
    with doc.create(Section('Education', numbering=False)):
        with doc.create(Subsection('Pg-Diploma in Big Data Analytics', numbering=False)):
            doc.append('Center for Development of Advanced Computing (CDAC), Pune | Sept 2021')

        with doc.create(Subsection('Bachelor of Engineering in Electronics & Telecommunication', numbering=False)):
            doc.append("Pune Vidyarthi Griha's College of Engineering, Nashik | June 2017")

        with doc.create(Subsection('Diploma in Electronics & Telecommunication', numbering=False)):
            doc.append("Maratha Vidya Prasarak Samaj's Rajarshi Shahu Maharaj Polytechnic, Nashik | June 2014")

        with doc.create(Subsection('10th School', numbering=False)):
            doc.append('Maratha High School, Nashik | 2011')

    # Projects
    with doc.create(Section('Projects', numbering=False)):
        with doc.create(Subsection('Socket Service', numbering=False)):
            with doc.create(Itemize()) as itemize:
                details = [
                    "Developed a scalable microservice to handle over 100,000 concurrent game players.",
                    "Utilized Kafka and Redis for efficient data transfer and management.",
                    "Designed a horizontally scalable system for adding servers to support an increasing number of players.",
                    "Implemented WebSocket for real-time communication."
                ]
                for detail in details:
                    itemize.add_item(detail)

        with doc.create(Subsection('Kibana Integration', numbering=False)):
            with doc.create(Itemize()) as itemize:
                details = [
                    "Integrated Kibana, Logstash, and Elasticsearch for game application data tracking.",
                    "Created Kibana dashboards to visualize trends, identify production issues, and understand game feature functionality.",
                    "Analyzed player data to provide insights for business decisions and improve the gaming experience.",
                    "Developed comprehensive monitoring and logging solutions to enhance system reliability."
                ]
                for detail in details:
                    itemize.add_item(detail)

    # Interests
    with doc.create(Section('Interests', numbering=False)):
        with doc.create(Itemize()) as itemize:
            interests = ["Reading", "Travel"]
            for interest in interests:
                itemize.add_item(interest)

    # Generate the PDF
    doc.generate_pdf('Pavan_Khairnar_ATS_Resume', clean_tex=False)

# Create the resume
create_resume()
