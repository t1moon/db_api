CLEAR_TABLE = u'''
                    TRUNCATE TABLE {} ;
                '''

RESET_AUTO_INCREMENT = u'''
                            ALTER TABLE {} AUTO_INCREMENT = 1 ;
                        '''

RESET_FK_CHECKS = u'''
                      SET FOREIGN_KEY_CHECKS = {} ;
                   '''


SELECT_TABLE_STATUSES = u'''
                            SELECT COUNT(*) FROM {}s;
                            '''
