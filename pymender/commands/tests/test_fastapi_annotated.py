from libcst.codemod import CodemodTest

from ..fastapi_annotated import FastAPIAnnotated

EXAMPLE_FUNCTION = """

@router.get('/example')
def example_function(
    value: int,
    query: str = Query("foo"),
    zar: str = Query(default="bar", alias="z"),
    foo: str = Depends(get_foo),
    *,
    bar: str = Depends(get_bar),
    body: str = Body(...),
) -> str:
    return 'example'
    
"""

EXAMPLE_FUNCTION_WITH_ANNOTATED = """
from typing import Annotated

@router.get('/example')
def example_function(
    value: int,
    foo: Annotated[str, Depends(get_foo)],
    query: Annotated[str, Query()] = "foo",
    zar: Annotated[str, Query(alias="z")] = "bar",
    *,
    bar: Annotated[str, Depends(get_bar)],
    body: Annotated[str, Body()],
) -> str:
    return 'example'

"""

EXAMPLE_ASYNC_FUNCTION = """
@contacts_enrich_industry_router.post(
    "/enrich-industry",
    response_model=list[SQSEvent[EnrichCompanyIndustrySchema]],
    status_code=status.HTTP_200_OK,
)
async def enrich_companies_with_industry(*, session: Session = Depends(get_session)):
    return []
"""

EXAMPLE_ASYNC_FUNCTION_CORRECT = """
from typing import Annotated

@contacts_enrich_industry_router.post(
    "/enrich-industry",
    response_model=list[SQSEvent[EnrichCompanyIndustrySchema]],
    status_code=status.HTTP_200_OK,
)
async def enrich_companies_with_industry(*, session: Annotated[Session, Depends(get_session)]):
    return []
"""


class TestFastAPIAnnotatedCommand(CodemodTest):
    # The codemod that will be instantiated for us in assertCodemod.
    TRANSFORM = FastAPIAnnotated

    def test_substitution(self) -> None:
        self.maxDiff = None
        self.assertCodemod(EXAMPLE_FUNCTION, EXAMPLE_FUNCTION_WITH_ANNOTATED)

    def test_async_sub(self) -> None:
        self.maxDiff = None
        self.assertCodemod(EXAMPLE_ASYNC_FUNCTION, EXAMPLE_ASYNC_FUNCTION_CORRECT)
