from fastapi import APIRouter

from backend.app.schemas.applicant import ApplicantInput
from backend.app.services.prediction_service import predict_risk

router = APIRouter(
    prefix="/predict",
    tags=["Credit Risk"]
)


def create_prediction_router(model):

    @router.post("")
    def predict(applicant: ApplicantInput):
        return predict_risk(
            model,
            applicant.model_dump()
        )

    return router