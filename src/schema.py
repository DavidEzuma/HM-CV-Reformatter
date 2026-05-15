from pydantic import BaseModel, Field
from typing import Optional


class Degree(BaseModel):
    institution: str
    degree: str
    field: Optional[str] = None
    year: Optional[str] = None


class Training(BaseModel):
    institution: str
    type: str  # residency / fellowship / postdoc
    specialty: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None


class Position(BaseModel):
    institution: str
    title: str
    department: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None  # "Present" if current


class License(BaseModel):
    state: str
    number: Optional[str] = None
    expiration: Optional[str] = None


class BoardCert(BaseModel):
    board: str
    specialty: str
    year: Optional[str] = None
    expiration: Optional[str] = None


class Grant(BaseModel):
    source: str          # NIH, NSF, etc.
    grant_number: Optional[str] = None
    title: str
    pi: Optional[str] = None
    role: Optional[str] = None  # PI / Co-I / Mentor
    dates: Optional[str] = None
    amount: Optional[str] = None


class Mentee(BaseModel):
    name: str
    degree: Optional[str] = None  # PhD, MD, etc.
    institution: Optional[str] = None
    dates: Optional[str] = None
    current_position: Optional[str] = None


class EditorialActivity(BaseModel):
    journal: str
    role: str  # Editor / Board Member / Reviewer
    dates: Optional[str] = None


class Presentation(BaseModel):
    title: str
    venue: str
    location: Optional[str] = None
    date: Optional[str] = None


class Publication(BaseModel):
    citation: str  # full formatted citation, bold candidate name


class HMCVData(BaseModel):
    # ── Header ────────────────────────────────────────────────────────────────
    name: str = Field(description="Full name with credentials e.g. Jane Doe, MD")
    date_of_preparation: Optional[str] = None

    # ── Personal Data ─────────────────────────────────────────────────────────
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    other_personal: Optional[str] = None

    # ── Education ─────────────────────────────────────────────────────────────
    academic_degrees: list[Degree] = Field(default_factory=list)
    other_educational_experiences: list[str] = Field(default_factory=list)

    # ── Postdoctoral Training ─────────────────────────────────────────────────
    postdoctoral_training: list[Training] = Field(default_factory=list)

    # ── Professional Positions ────────────────────────────────────────────────
    academic_appointments: list[Position] = Field(default_factory=list)
    hospital_appointments: list[Position] = Field(default_factory=list)
    other_positions: list[Position] = Field(default_factory=list)

    # ── Employment Status ─────────────────────────────────────────────────────
    current_employer: Optional[str] = None
    employment_status: Optional[str] = None

    # ── Licensure & Certification ─────────────────────────────────────────────
    licensure: list[License] = Field(default_factory=list)
    board_certifications: list[BoardCert] = Field(default_factory=list)

    # ── Affiliations ──────────────────────────────────────────────────────────
    institutional_affiliations: list[str] = Field(default_factory=list)

    # ── Honors & Awards ───────────────────────────────────────────────────────
    honors_awards: list[str] = Field(default_factory=list)

    # ── Professional Organizations ────────────────────────────────────────────
    professional_organizations: list[str] = Field(default_factory=list)

    # ── Percent Effort ────────────────────────────────────────────────────────
    percent_effort_clinical: Optional[str] = None
    percent_effort_research: Optional[str] = None
    percent_effort_teaching: Optional[str] = None
    percent_effort_admin: Optional[str] = None

    # ── Educational Contributions ─────────────────────────────────────────────
    didactic_teaching: list[str] = Field(default_factory=list)
    clinical_teaching: list[str] = Field(default_factory=list)
    administrative_teaching: list[str] = Field(default_factory=list)
    continuing_education: list[str] = Field(default_factory=list)
    other_education: list[str] = Field(default_factory=list)

    # ── Clinical ──────────────────────────────────────────────────────────────
    clinical_practice: Optional[str] = None
    clinical_innovations: Optional[str] = None
    clinical_leadership: Optional[str] = None

    # ── Research ──────────────────────────────────────────────────────────────
    research_activities: Optional[str] = None
    current_funding: list[Grant] = Field(default_factory=list)
    past_funding: list[Grant] = Field(default_factory=list)
    pending_funding: list[Grant] = Field(default_factory=list)
    patents: list[str] = Field(default_factory=list)

    # ── Mentoring ─────────────────────────────────────────────────────────────
    current_mentees: list[Mentee] = Field(default_factory=list)
    past_mentees: list[Mentee] = Field(default_factory=list)
    training_grants: list[str] = Field(default_factory=list)

    # ── Leadership & Admin ────────────────────────────────────────────────────
    institutional_leadership: list[str] = Field(default_factory=list)
    institutional_administrative: list[str] = Field(default_factory=list)

    # ── Extramural ────────────────────────────────────────────────────────────
    extramural_leadership: list[str] = Field(default_factory=list)
    boards_committees_regional: list[str] = Field(default_factory=list)
    boards_committees_national: list[str] = Field(default_factory=list)
    boards_committees_international: list[str] = Field(default_factory=list)
    grant_reviewing: list[str] = Field(default_factory=list)
    editorial_editor: list[EditorialActivity] = Field(default_factory=list)
    editorial_board: list[EditorialActivity] = Field(default_factory=list)
    editorial_reviewer: list[EditorialActivity] = Field(default_factory=list)

    # ── Invitations to Speak ──────────────────────────────────────────────────
    presentations_regional: list[Presentation] = Field(default_factory=list)
    presentations_national: list[Presentation] = Field(default_factory=list)
    presentations_international: list[Presentation] = Field(default_factory=list)

    # ── Bibliography ──────────────────────────────────────────────────────────
    peer_reviewed_articles: list[Publication] = Field(default_factory=list)
    reviews_editorials: list[Publication] = Field(default_factory=list)
    books: list[Publication] = Field(default_factory=list)
    chapters: list[Publication] = Field(default_factory=list)
    non_peer_reviewed: list[Publication] = Field(default_factory=list)
    case_reports: list[Publication] = Field(default_factory=list)
    in_review: list[Publication] = Field(default_factory=list)
    abstracts: list[Publication] = Field(default_factory=list)
    other_publications: list[Publication] = Field(default_factory=list)
