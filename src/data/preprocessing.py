"""
Data preprocessing module for ENEM data.
"""

import pandas as pd
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data type mappings
DTYPE_MAPPINGS = {
    'NU_INSCRICAO': 'int64',
    'NU_ANO': 'int16',
    'TP_FAIXA_ETARIA': 'int8',
    'TP_SEXO': 'category',
    'TP_ESTADO_CIVIL': 'category',
    'TP_COR_RACA': 'category',
    'TP_NACIONALIDADE': 'category',
    'TP_ST_CONCLUSAO': 'category',
    'TP_ANO_CONCLUIU': 'int16',
    'TP_ESCOLA': 'category',
    'NU_NOTA_CN': 'float32',
    'NU_NOTA_CH': 'float32',
    'NU_NOTA_LC': 'float32',
    'NU_NOTA_MT': 'float32',
    'NU_NOTA_REDACAO': 'float32'
}

# Category mappings
CATEGORY_MAPPINGS = {
    'TP_SEXO': {
        'M': 'Male',
        'F': 'Female'
    },
    'TP_ESTADO_CIVIL': {
        0: 'Not Informed',
        1: 'Single',
        2: 'Married',
        3: 'Divorced',
        4: 'Widowed'
    },
    'TP_COR_RACA': {
        0: 'Not Declared',
        1: 'White',
        2: 'Black',
        3: 'Brown',
        4: 'Yellow',
        5: 'Indigenous'
    },
    'TP_NACIONALIDADE': {
        0: 'Not Informed',
        1: 'Brazilian',
        2: 'Brazilian Naturalized',
        3: 'Foreign',
        4: 'Brazilian Born Abroad'
    },
    'TP_ST_CONCLUSAO': {
        1: 'Completed',
        2: 'Completing This Year',
        3: 'Not Completed Yet',
        4: 'Not Completed'
    },
    'TP_ESCOLA': {
        1: 'Not Informed',
        2: 'Public',
        3: 'Private',
    }
}


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize data types for memory efficiency.
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with optimized data types
    """
    logger.info("Optimizing data types")

    for col, dtype in DTYPE_MAPPINGS.items():
        if col in df.columns:
            try:
                df[col] = df[col].astype(dtype)
                logger.debug(f"Converted {col} to {dtype}")
            except Exception as e:
                logger.warning(f"Could not convert {col} to {dtype}: {str(e)}")

    return df


def map_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map categorical variables to their descriptive values.
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with mapped categories
    """
    logger.info("Mapping categorical variables")

    for col, mapping in CATEGORY_MAPPINGS.items():
        if col in df.columns:
            try:
                df[col] = df[col].map(mapping).fillna('Unknown')
                logger.debug(f"Mapped categories for {col}")
            except Exception as e:
                logger.warning(f"Could not map categories for {col}: {str(e)}")

    return df


def handle_missing_values(
        df: pd.DataFrame,
        numeric_strategy: str = 'mean',
        categorical_strategy: str = 'mode'
) -> Tuple[pd.DataFrame, Dict]:
    """
    Handle missing values in the dataset.
    
    Args:
        df: Input DataFrame
        numeric_strategy: Strategy for numeric columns ('mean', 'median', 'zero')
        categorical_strategy: Strategy for categorical columns ('mode', 'unknown')
    
    Returns:
        Tuple of (cleaned DataFrame, dictionary with imputation values)
    """
    logger.info("Handling missing values")

    imputation_values = {}

    # Handle numeric columns
    numeric_cols = df.select_dtypes(include=['int', 'float']).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            if numeric_strategy == 'mean':
                value = df[col].mean()
            elif numeric_strategy == 'median':
                value = df[col].median()
            else:
                value = 0

            df[col] = df[col].fillna(value)
            imputation_values[col] = value
            logger.debug(f"Imputed {col} with {value}")

    # Handle categorical columns
    cat_cols = df.select_dtypes(include=['category', 'object']).columns
    for col in cat_cols:
        if df[col].isnull().any():
            if categorical_strategy == 'mode':
                value = df[col].mode()[0]
            else:
                value = 'Unknown'

            df[col] = df[col].fillna(value)
            imputation_values[col] = value
            logger.debug(f"Imputed {col} with {value}")

    return df, imputation_values


def validate_data(df: pd.DataFrame) -> List[str]:
    """
    Validate data quality and constraints.
    
    Args:
        df: Input DataFrame
    
    Returns:
        List of validation issues found
    """
    logger.info("Validating data")

    issues = []

    # Check score ranges
    score_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']
    for col in score_cols:
        if col in df.columns:
            invalid_scores = df[df[col].notna() & ((df[col] < 0) | (df[col] > 1000))][col]
            if len(invalid_scores) > 0:
                issues.append(f"Found {len(invalid_scores)} invalid scores in {col}")

    # Check essay scores
    if 'NU_NOTA_REDACAO' in df.columns:
        invalid_essays = df[df['NU_NOTA_REDACAO'].notna() &
                            ((df['NU_NOTA_REDACAO'] < 0) |
                             (df['NU_NOTA_REDACAO'] > 1000))]['NU_NOTA_REDACAO']
        if len(invalid_essays) > 0:
            issues.append(f"Found {len(invalid_essays)} invalid essay scores")

    # Check age ranges
    if 'TP_FAIXA_ETARIA' in df.columns:
        invalid_ages = df[df['TP_FAIXA_ETARIA'] < 1]['TP_FAIXA_ETARIA']
        if len(invalid_ages) > 0:
            issues.append(f"Found {len(invalid_ages)} invalid age ranges")

    return issues


def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features from existing data.
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with additional derived features
    """
    logger.info("Creating derived features")

    # Average score
    score_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']
    if all(col in df.columns for col in score_cols):
        df['AVERAGE_SCORE'] = df[score_cols].mean(axis=1)
        logger.debug("Created AVERAGE_SCORE feature")

    # Score standard deviation (consistency measure)
    if all(col in df.columns for col in score_cols):
        df['SCORE_STD'] = df[score_cols].std(axis=1)
        logger.debug("Created SCORE_STD feature")

    # Best and worst subjects
    if all(col in df.columns for col in score_cols):
        df['BEST_SUBJECT'] = df[score_cols].idxmax(axis=1).map({
            'NU_NOTA_CN': 'Natural Sciences',
            'NU_NOTA_CH': 'Human Sciences',
            'NU_NOTA_LC': 'Languages',
            'NU_NOTA_MT': 'Mathematics'
        })
        df['WORST_SUBJECT'] = df[score_cols].idxmin(axis=1).map({
            'NU_NOTA_CN': 'Natural Sciences',
            'NU_NOTA_CH': 'Human Sciences',
            'NU_NOTA_LC': 'Languages',
            'NU_NOTA_MT': 'Mathematics'
        })
        logger.debug("Created BEST_SUBJECT and WORST_SUBJECT features")

    return df
