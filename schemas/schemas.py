""" Pydantic schemas for the app
"""
from datetime import datetime
from typing import Dict, List, Literal, Optional, Union, Callable
from pydantic import BaseModel

class Args(BaseModel):
    """Command line arguments"""
    lang: Optional[List[str]]
    filter: Optional[List[str]]
    email: bool = False
    send: bool = False
    write: bool = False

class Progress(BaseModel):
    progressbar: Callable
    label: Callable
    
class ApplicationContact(BaseModel):
    contact_type: Optional[str]
    description: Optional[str]
    email: Optional[str]
    name: Optional[str]
    telephone: Optional[str]
    
    
class ApplicationDetails(BaseModel):
    email: Optional[str]
    information: Optional[str]
    other: Optional[str]
    reference: Optional[str]
    url: Optional[str]
    via_af: bool
    
    
class Description(BaseModel):
    company_information: Optional[str]
    conditions: Optional[str]
    needs: Optional[str]
    requirements: Optional[str]
    text: str
    text_formatted: str
    
    
class Concept(BaseModel):
    concept_id: Optional[str]
    label: Optional[str]
    legacy_ams_taxonomy_id: Optional[str]
    
    
class WeighedConcept(Concept):
    weight: Optional[float]
    
    
class Employer(BaseModel):
    email: Optional[str]
    name: Optional[str]
    organisation_number: Optional[str]
    phone_number: Optional[str]
    url: Optional[str]
    workplace: Optional[str]
    
    
class Preferences(BaseModel):
    education: Optional[List[WeighedConcept]]
    education_level: Optional[List[WeighedConcept]]
    languages: Optional[List[WeighedConcept]]
    skills: Optional[List[WeighedConcept]]
    work_experiences: Optional[List[WeighedConcept]]
    
    
class Scope(BaseModel):
    max: Optional[int]
    min: Optional[int]
    
    
class Workplace(BaseModel):
    """Model for workplace field in ad
    """
    city: Optional[str]
    coordinates: Optional[List[float]]
    country: Optional[str]
    country_code: Optional[str]
    country_concept_id: Optional[str]
    municipality: Optional[str]
    municipality_concept_id: Optional[str]
    postcode: Optional[str]
    region: Optional[str]
    region_code: Optional[str]
    region_concept_id: Optional[str]
    street_address: Optional[str]
    
    
class Ad(BaseModel):
    """Ad model
    """
    access: Optional[str]
    access_to_own_car: bool
    application_contacts: List[ApplicationContact]
    application_deadline: datetime
    application_details: ApplicationDetails
    description: Description
    driving_license: Optional[List[Concept]]
    driving_license_required: bool
    duration: Concept
    employer: Employer
    employment_type: Concept
    experience_required: bool
    external_id: Optional[str]
    headline: str
    id: str
    language: Optional[str]
    last_publication_date: str
    logo_url: Optional[str]
    must_have: Preferences
    nice_to_have: Preferences
    number_of_vacancies: int
    occupation: Concept
    occupation_field: Concept
    occupation_group: Concept
    publication_date: datetime
    relevance: float
    removed: bool
    removed_date: Optional[datetime]
    salary_description: Optional[str]
    salary_type: Concept
    scope_of_work: Scope
    source_type: str
    timestamp: int
    webpage_url: str
    working_hours_type: Concept
    workplace_address: Workplace


class EmailAttachments(BaseModel):
    CV: str
    CoverLetter: str

class EmailParams(BaseModel):
    recipient: str
    subject: str
    body: str
    attachments: EmailAttachments

class SearchParams(BaseModel):
    q: str
    offset: Optional[int]
    limit: Optional[int]
    remote: Optional[bool]
    qfields: Optional[List[Literal['occupation', 'skill', 'location', 'employer']]]
    relevance_threshold: Optional[float]
    resdet: Optional[Literal['full', 'brief']]
    sort: Optional[Literal['relevance', 'pubdate-desc', 'pubdate-asc', 'applydate-desc', 'applydate-asc', 'updated', 'id']]
    stats: Optional[Literal['occupation-name', 'occupation-group', 'occupation-field', 'country', 'municipality', 'region']]
    open_for_all: Optional[bool]
    country: Optional[List[str]]
    region: Optional[List[str]]
    municipality: Optional[List[str]]
    experience: Optional[bool]
    language: Optional[List[str]]
    
    
class QueryParams(SearchParams):
    total: int

class SearchTotal(BaseModel):
    value: int

class QStatDetail(BaseModel):
    term: str
    concept_id: str
    code: str
    count: int

class QStats(BaseModel):
    type: str
    values: List[QStatDetail]

class QueryResponse(BaseModel):
    total: SearchTotal
    positions: int
    query_time_in_millis: int
    result_time_in_millis: int
    stats: Optional[List[QStats]]
    freetext_concepts: Optional[Dict[str, List]]
    hits: List[Ad]

class ClientHistory(BaseModel):
    responses: Optional[List[QueryResponse]]
    params: Optional[List[SearchParams]]
    total_received: Optional[int]
    args: Optional[List[Args]]
    errors: Optional[List[str]]

class ClientStatus(BaseModel):
    code: Literal[0,1,2,3]
    message: Optional[str]
    expecting: Optional[int]
    received: Optional[int]
    errors: Optional[int]