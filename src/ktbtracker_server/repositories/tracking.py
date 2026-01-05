from datetime import date, timedelta
from typing import Sequence, Annotated

from fastapi import Depends
from sqlmodel import DOUBLE, Session, func, select

from ktbtracker_server.config.mysql import get_session
from ktbtracker_server.entities import entities


class TrackingRepository:
    def __init__(self, session: Session):
        self.session = session

    def calculate_full_statistics(
            self,
            candidate_id: int,
    ) -> entities.FullStatistics:
        if candidate := self.session.exec(select(entities.Candidate)
                                                  .where(entities.Candidate.id == candidate_id)
                                          ).first():
            full_statistics = entities.FullStatistics(
                candidate_id=candidate_id,
                start_date=candidate.cycle.cycle_start,
                end_date=candidate.cycle.cycle_end,
            )
            for cycle_week in range(candidate.cycle.cycle_weeks):
                week_start = candidate.cycle.cycle_start + timedelta(days=cycle_week * 7)
                week_end = week_start + timedelta(days=7)
                full_statistics.weeks.append(self.calculate_statistics(candidate_id, week_start, week_end))
            # Calculate Cycle Overall
            sum(w.overall for w in full_statistics.weeks) / len(full_statistics.weeks) if full_statistics.weeks else 0.0

            return full_statistics

        return entities.FullStatistics(candidate_id=candidate_id, start_date=date.today(), end_date=date.today())

    def calculate_statistics(
            self,
            candidate_id: int,
            start_date: date,
            end_date: date,
    ):
        if candidate := self.session.exec(select(entities.Candidate)
                                                  .where(entities.Candidate.id == candidate_id)).first():
            statistics = entities.Statistics(
                candidate_id=candidate_id,
                start_date=start_date,
                end_date=end_date,
                totals=self.calculate_totals(candidate.id, start_date, end_date))
            statistics.calculate(candidate.cycle)

            return statistics

        return entities.Statistics(candidate_id=candidate_id, start_date=start_date, end_date=end_date)

    def calculate_totals(
            self,
            candidate_id: int,
            start_date: date,
            end_date: date,
    ) -> entities.TrackingFields:
        result = (self.session.exec(
            select(
                func.cast(func.coalesce(func.sum(entities.Tracking.burpees), 0), DOUBLE).label('burpees'),
                func.cast(func.coalesce(func.sum(entities.Tracking.class_dream_team), 0), DOUBLE).label('class_dream_team'),
                func.cast(func.coalesce(func.sum(entities.Tracking.class_hyper_pro), 0), DOUBLE).label('class_hyper_pro'),
                func.cast(func.coalesce(func.sum(entities.Tracking.class_master_q), 0), DOUBLE).label('class_master_q'),
                func.cast(func.coalesce(func.sum(entities.Tracking.class_pmaa), 0), DOUBLE).label('class_pmaa'),
                func.cast(func.coalesce(func.sum(entities.Tracking.class_saturday), 0), DOUBLE).label('class_saturday'),
                func.cast(func.coalesce(func.sum(entities.Tracking.class_sparring), 0), DOUBLE).label('class_sparring'),
                func.cast(func.coalesce(func.sum(entities.Tracking.class_weekday), 0), DOUBLE).label('class_weekday'),
                func.cast(func.coalesce(func.sum(entities.Tracking.jumps), 0), DOUBLE).label('jumps'),
                func.cast(func.coalesce(func.sum(entities.Tracking.kicks), 0), DOUBLE).label('kicks'),
                func.cast(func.coalesce(func.sum(entities.Tracking.leadership), 0), DOUBLE).label('leadership'),
                func.cast(func.coalesce(func.sum(entities.Tracking.leadership2), 0), DOUBLE).label('leadership2'),
                func.cast(func.coalesce(func.sum(entities.Tracking.meditation), 0), DOUBLE).label('meditation'),
                func.cast(func.coalesce(func.sum(entities.Tracking.mentee), 0), DOUBLE).label('mentee'),
                func.cast(func.coalesce(func.sum(entities.Tracking.mentor), 0), DOUBLE).label('mentor'),
                func.cast(func.coalesce(func.sum(entities.Tracking.miles), 0), DOUBLE).label('miles'),
                func.cast(func.coalesce(func.sum(entities.Tracking.planks), 0), DOUBLE).label('planks'),
                func.cast(func.coalesce(func.sum(entities.Tracking.poomsae), 0), DOUBLE).label('poomsae'),
                func.cast(func.coalesce(func.sum(entities.Tracking.pull_ups), 0), DOUBLE).label('pull_ups'),
                func.cast(func.coalesce(func.sum(entities.Tracking.push_ups), 0), DOUBLE).label('push_ups'),
                func.cast(func.coalesce(func.sum(entities.Tracking.raok), 0), DOUBLE).label('raok'),
                func.cast(func.coalesce(func.sum(entities.Tracking.rolls_falls), 0), DOUBLE).label('rolls_falls'),
                func.cast(func.coalesce(func.sum(entities.Tracking.self_defense), 0), DOUBLE).label('self_defense'),
                func.cast(func.coalesce(func.sum(entities.Tracking.sit_ups), 0), DOUBLE).label('sit_ups'),
                func.cast(func.coalesce(func.sum(entities.Tracking.sparring), 0), DOUBLE).label('sparring')
            ).where(
                entities.Tracking.candidate_id == candidate_id,
                entities.Tracking.tracking_date >= start_date,
                entities.Tracking.tracking_date <= (end_date or start_date)
            )
        )).first()

        return entities.TrackingFields.model_validate(result)

    def find_all_by_candidate_id_and_date(
            self,
            candidate_id: int,
            tracking_date: date,
    ) -> entities.Tracking:
        return self.session.exec(select(entities.Tracking)
                                 .where(entities.Tracking.candidate_id == candidate_id,
                                        entities.Tracking.tracking_date == tracking_date)
                                 ).first()

    def find_all_by_candidate_id_and_date_range(
            self,
            candidate_id: int,
            start_date: date,

            end_date: date,
    ) -> Sequence[entities.Tracking]:
        return self.session.exec(select(entities.Tracking)
                                 .where(entities.Tracking.candidate_id == candidate_id,
                                        entities.Tracking.tracking_date >= start_date,
                                        entities.Tracking.tracking_date <= (end_date or start_date))
                                 ).all()

    def find_candidate_by_id(
            self,
            id: int
    ) -> entities.Candidate:
        return self.session.exec(select(entities.Candidate)
                                 .where(entities.Candidate.id == id)
                                 ).first()


async def get_tracking_repository(session: Annotated[Session, Depends(get_session)]):
    return TrackingRepository(session)
