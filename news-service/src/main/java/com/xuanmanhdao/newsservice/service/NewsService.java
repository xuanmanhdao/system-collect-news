package com.xuanmanhdao.newsservice.service;

import com.xuanmanhdao.newsservice.entity.NewsDocumentEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface NewsService {
    Iterable<NewsDocumentEntity> getAll();

    Page<NewsDocumentEntity> searchByTitle(String keyword, Pageable pageable);

    Page<NewsDocumentEntity> searchBySource(String source, Pageable pageable);
}
