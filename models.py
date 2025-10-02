from sqlalchemy import Column, Integer, LargeBinary, String, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from config import Base

class Subject(Base):
    __tablename__ = "subject"
    
    subjectid = Column(Integer, primary_key=True)
    subjectname = Column(String(50), nullable=False)
    subjectinfo = Column(Text, nullable=True)
    
    students = relationship("Student", back_populates="subject")


class Student(Base):
    __tablename__ = "student"

    studentid = Column(BigInteger, primary_key=True)
    studentname = Column(LargeBinary, nullable=False)  # encrypted
    fk_subjectid = Column(BigInteger, ForeignKey("subject.subjectid", ondelete="CASCADE"))

    subject = relationship("Subject", back_populates="students")        