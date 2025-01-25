# Senior Design Project

This is a project completed in a team of 6 from September 2024 - May 2025 and is the culmination of knowledge gained from our computer science undergraduate education.

## Goal

Develop an internet based app tailored to the iPhone that automates the reading and calculation of score cards for the South Eastern Distance Riders Association.

## Problem

Distance riding events are competitions in which horse and rider pairs compete over distances of 25 to 100 miles. The goal of each rider is to complete the full distance within an allotted time with a healthy and sound horse. Each event is split into two or more segments of approximately 10-20 miles. Horses are evaluated on soundness after each segment and are only allowed to continue to the next segment if they pass the vet check. These soundness evaluations are used to determine the final scores.

Two scorecards are typically used: CTR to judge a single entrant, and BC to judge multiple entrants.

## Solution

A web based app that will allow a user to use their iPhone to take a photo of a score card, use computer vision/machine learning techniques to read the written values on the scorecard, allow the user to review (and correct if needed) the values read in, and then calculate and display the results.

## Stated Requirements

The minimum required functionality is a web-app that can read each of the two forms and calculate the score results.

Functionality required for CTR score cards:
1. Input CTR score card via photo.
2. Segment out the image patch for each value that is to be read.
3. Use computer vision methods (or machine learning/deep learning) to read the hand written values in each of the image segments.
4. Display the values read in to the user for verification. Indicate values interpreted with low certainty (that require extra user attention) in red or otherwise highlight. Display all values in editable textboxes on a single page that the user can edit if any corrections are needed. Do not require the user to go to a separate page to edit each value.
5. Calculate score and display result. Score calculation entails summing all penalty points and subtracting the sum from 100.

Functionality required for BC score cards:
1. Ask user to enter ride parameters.
2. Ask user to enter the number of BC score cards for event. Each event will have one or more BC score cards and each card contains data for one to five entrants.
3. Input all score cards via photo(s).
4. Segment out the image patch for each value that is to be read.
5. Use computer vision methods (or machine learning/deep learning) to read the hand written values in each of the image segments.
6. Display the values read in to the user for verification. Indicate values interpreted with low certainty (that require extra user attention) in red or otherwise highlight. Because there will likely be more than one rider, in the user verification phase, display the data for one rider at a time, each on a single page. Display each value in an editable textbox that the user can edit if corrections are needed. Do not require the user to go to a separate page to edit each value.
7. Once all rider scores have been verified, calculate and display result. The instructions for calculating the result are given in Appendix C. The calculation requires knowledge of the fastest time and the heaviest rider; as a result, the result can only be calculated after all rider data has been read in.

Must include documentation of the code.