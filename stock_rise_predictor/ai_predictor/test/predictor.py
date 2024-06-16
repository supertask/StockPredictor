# coding=utf-8
 
class ScoringService(object):
    
    @classmethod
    def get_model(cls, model_path='../model'):
        """Get model method
 
        Args:
            model_path (str): Path to the trained model directory.
 
        Returns:
            bool: The return value. True for success, False otherwise.
 
        """
        return True
 
    @classmethod
    def predict(cls, input):
        """Predict method
 
        Args:
            input (bytes): Input data for which you want the model to provide inference.
 
        Returns:
            str: Inference for the given input.
             
        """
        return 'ok'
