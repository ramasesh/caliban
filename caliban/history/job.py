'''job base'''

import uuid

from dateutil.tz import tzlocal
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any, Iterable, Union
from caliban.history.types import Platform, JobStatus
from caliban.history.interfaces import Experiment, Job, Run, Storage, ComputePlatform
import caliban.config as conf

import sys


# ----------------------------------------------------------------------------
class JobBase(Job):
  '''(abstract) base for Job

  provides:
    DictSerializable, Timestamped, Id, Named, User
    command(), args(), kwargs(), env()

  does not provide:
    experiment(), runs()
  '''

  def __init__(
      self,
      d: Dict[str, Any],
  ):
    self._id = d['id']
    self._name = d['name']
    self._user = d['user']
    self._timestamp = d['timestamp']
    self._args = d['args']
    self._kwargs = d['kwargs']
    self._experiment = d['experiment']

  def to_dict(self) -> Dict[str, Any]:
    '''serializes object to dictionary'''
    return self.create_dict(
        id=self._id,
        user=self._user,
        name=self._name,
        timestamp=self._timestamp,
        args=self._args,
        kwargs=self._kwargs,
        experiment=self._experiment,
    )

  def timestamp(self) -> datetime:
    '''returns timestamp that object was created'''
    return self._timestamp

  def user(self) -> str:
    '''returns user that created this object'''
    return self._user

  def id(self) -> str:
    '''returns object id'''
    return self._id

  def name(self) -> str:
    '''returns the name of this object'''
    return self._name

  def args(self) -> List[str]:
    '''returns command positional args'''
    return self._args

  def kwargs(self) -> Dict[str, str]:
    '''returns command keyword args'''
    return self._kwargs

  @classmethod
  def create_dict(
      cls,
      id: str,
      name: str,
      user: str,
      timestamp: datetime,
      experiment: str,
      args: Optional[List[str]],
      kwargs: Optional[Dict[str, Any]],
  ) -> Dict[str, Any]:
    '''creates a JobBase dictionary'''
    return {
        'id': id,
        'user': user,
        'name': name,
        'timestamp': timestamp,
        'experiment': experiment,
        'args': args or [],
        'kwargs': kwargs or {}
    }

  @classmethod
  def create_dicts(
      cls,
      name: str,
      user: str,
      experiment: str,
      configs: Optional[List[conf.Experiment]] = None,
      args: Optional[List[str]] = None,
  ) -> Iterable[Dict[str, Any]]:
    '''create Job dictionaries from configs and args'''

    if configs is None or len(configs) == 0:
      configs = [{}]

    for i, c in enumerate(configs):
      yield cls.create_dict(
          id=uuid.uuid1().hex,
          name=name + '-{}'.format(i),
          user=user,
          timestamp=datetime.now(tz=tzlocal()),
          experiment=experiment,
          args=args,
          kwargs={k: v for k, v in configs[i].items()},
      )


# ----------------------------------------------------------------------------
class StorageJob(JobBase):
  '''storage-backed job'''

  def __init__(
      self,
      storage: Storage,
      d: Dict[str, Any],
      create: bool = False,
  ):
    super().__init__(d)
    self._storage = storage

  def runs(self) -> Iterable[Run]:
    return self._storage.collection('runs').where('job', QueryOp.EQ, self.id())

  def experiment(self) -> Experiment:
    return self._storage.collection('experiments').get(self._experiment)