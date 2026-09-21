from fastapi import APIRouter, Depends

from backend.app.services.auth_service import require_role
from backend.app.schemas.applicant import ApplicantInput
from backend.app.services.prediction_service import predict_risk


router = APIRouter(
    prefix="/predict",
    tags=["Credit Risk"]
)


def create_prediction_router(model):

    @router.post("")
    def predict(
        applicant: ApplicantInput,
        current_user=Depends(require_role("ANALYST")),
    ):
        return predict_risk(
            model,
            applicant.model_dump()
        )

    return router