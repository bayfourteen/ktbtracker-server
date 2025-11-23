from datetime import date, timedelta
from typing import Annotated, Sequence

from fastapi import Depends

from models import models

from repositories.tracking import TrackingRepository, get_tracking_repository


class TrackingService:
    def __init__(self, repository: TrackingRepository):
        self.repository = repository

    def calculate_totals(
            self,
            candidate_id: int,
            start_date: date,
            end_date: date,
    ) -> models.TrackingTotals:
        return models.TrackingTotals(
            candidate_id=candidate_id,
            start_date=start_date,
            end_date=end_date,
            totals=models.TrackingFields.model_validate(
                self.repository.calculate_totals(candidate_id, start_date, end_date)))

    def calculate_full_statistics(
            self,
            candidate_id: int,
    ) -> models.FullStatistics:
        if candidate := self.repository.find_candidate_by_id(candidate_id):
            full_statistics = models.FullStatistics.model_validate(
                self.repository.calculate_statistics(
                    candidate.id, candidate.cycle.cycle_start, candidate.cycle.cycle_end))

            # Calculate Statistics for each week in the cycle
            for cycle_week in range(candidate.cycle.cycle_weeks):
                week_start = candidate.cycle.cycle_start + timedelta(days=cycle_week * 7)
                week_end = week_start + timedelta(days=7)
                full_statistics.weeks.append(
                    models.Statistics.model_validate(self.calculate_statistics(candidate_id, week_start, week_end)))

            # Calculate Cycle Overall
            sum(w.overall for w in full_statistics.weeks) / len(full_statistics.weeks) if full_statistics.weeks else 0.0

            return full_statistics

        return models.FullStatistics(candidate_id=candidate_id, start_date=date.today(), end_date=date.today())

    def calculate_statistics(
            self,
            candidate_id: int,
            start_date: date,
            end_date: date,
    ) -> models.Statistics:
        return models.Statistics.model_validate(self.repository.calculate_statistics(candidate_id, start_date, end_date))

    def find_all_by_candidate_id_and_date_range(
            self,
            candidate_id: int,
            start_date: date,
            end_date: date,
    ) -> Sequence[models.Tracking]:
        return [
                models.Tracking.model_validate(e) for e in self.repository.find_all_by_candidate_id_and_date_range(candidate_id, start_date, end_date)
            ]


async def get_tracking_service(repository: Annotated[TrackingRepository, Depends(get_tracking_repository)]):
    return TrackingService(repository)
