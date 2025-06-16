class FailAddingProduct(Exception):
    pass

class ParameterError(Exception):
    def __str__():
        return "Both or no id/data provideded."    

# HTTP resposes
class Response(Exception):
    def __init__(self, code, status):
        self.code = code
        self.status = status
    
    def __str__(self):
        return f"{self.code}: {self.status}"
   
# Response for succeffully completed request 
class RequestComplete(Response):
    def __init__(self, response_data):
        code = 200
        status = "Ok"
        self.content = ({"Code": code, "Status": status, "Content": response_data}, code)

        super().__init__(code, status)

# Error response requisites
class RequestError(Response):
    def __init__(self, code, message, status):
        self.message = message
        self.content = ({"Code": code, "Status:": status, "Message": message}, code)

        super().__init__(code, status)   
        
    def __str__(self):
        return  f"[{self.code}: {self.status}] {self.message}"

# Especific Request Errors
class Unauthorized(RequestError):
    def __init__(self):
        code = 401
        status = "Unauthorized."
        message = "You don't have permission to access that resource"  

        super().__init__(code, message, status)
               
class UnprocessableEntity(RequestError):
    def __init__(self):
        code = 422
        status = "Unprocessable Entity"
        message = "Data doesn't match the expected format."
        super().__init__(code, message, status)
        
class InternalError(RequestError):
    def __init__(self):
        code = 500
        status = "Internal Server Error"
        message = "Server encontered an error adding the product, please review the the data."
        super().__init__(code, message, status)
        
class UnsupportedMediaType(RequestError):
    def __init__(self):
        code = 415
        status = "Unsupported Media Type"
        message = "Not supported Content-Type"
        super().__init__(code, message, status)
        
class ExceptionalError(RequestError):
    def __init__(self):
        code = 500
        status = "Internal Server Error"
        message = "Server encontered an uncaught error, please contact the administrator"
        super().__init__(code, message, status)
        
class QueryNotSupported(RequestError):
    def __init__(self):
        code = 400
        status = "Bad Request"
        message = "Not recognized query type."
        super().__init__(code, message, status)
        
class ProductNotFound(RequestError):
    def __init__(self):
        code = 404
        status = "Not Found"
        message = "Wasn't possible find the requested product, check the identifier."
        super().__init__(code, message, status)
        
class NotImplementedYet(RequestError):
    def __init__(self):
        code = 404
        status = "Not implemented yet"
        message = "The functionallity that you tried to access are not available yet."
        super().__init__(code, message, status)

class ProductAlredyExists(RequestError):
    def __init__(self):
        code = 409
        status = "Conflict"
        message = "The product alredy exists in the database or the url is duplicated."
        super().__init__(code, message, status)
        
class ProductInactive(RequestError):
    def __init__(self):
        code = 410
        status = "Gone"
        message = "The product is inactive."
        super().__init__(code, message, status)
        
class NoParameter(RequestError):
    def __init__(self, parameters):
        code = 400
        status = "Bad Request"
        message = f"Parameter(s): {parameters} missing."
        super().__init__(code, message, status)
        