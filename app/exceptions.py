class PrismaVitaeError(Exception):
    """Error base de dominio. `status_code` define el HTTP que se devuelve."""

    status_code = 400


class NotFoundError(PrismaVitaeError):
    status_code = 404


class AuthError(PrismaVitaeError):
    status_code = 401


class ForbiddenError(PrismaVitaeError):
    status_code = 403


class ValidationError(PrismaVitaeError):
    status_code = 422


class ExtractionError(PrismaVitaeError):
    status_code = 500


class StorageError(PrismaVitaeError):
    status_code = 500